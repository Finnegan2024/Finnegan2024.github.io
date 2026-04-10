## This file contains all of the code needed to measure benchmarks to compare uniform and prioritized experience replay (PER) buffers
## Measures end to end DQN training to demonstrate the practical performance enhancement using a simple DQN
## I attempted to contain most code for the benchmark measurements in this file to avoid disparities between the older and newer DQN and to ensure consistency

import time
import csv
import numpy as np
import tensorflow as tf
import random
from keras.models import Sequential
from keras.layers import Dense, Activation, PReLU

from Experience import Experience as uniform
from Prioritized_Experience_Replay import PER
from Qmaze import Qmaze


# This creates fake transitions to ensure we measure uniform and prioritized replay buffers using the same set of data
def make_fake_transitions(envSize, numActions):
    state = np.random.rand(1, envSize)
    action = np.random.randint(0, numActions)
    reward = np.random.choice([1.0, -33.0, -0.25, -0.75, -0.04])
    next_state = np.random.rand(1, envSize)
    done = np.random.rand() < 0.1
    return [state, action, reward, next_state, done]


# copy of DQN model from original and enhanced artifacts
def model(envSize, numActions):
    model = Sequential()
    model.add(Dense(envSize, input_shape=(envSize,)))
    model.add(PReLU())
    model.add(Dense(envSize))
    model.add(PReLU())
    model.add(Dense(numActions))
    model.compile(optimizer='adam', loss='mse')
    return model


# this measure the time it takes to insert new episodes in the PER
def benchmark_insert(buffer, transitions):
    start = time.perf_counter()
    for transition in transitions:
        buffer.remember(transition)
    end = time.perf_counter()
    return end - start


def benchmark_sampling(buffer, batchSize, numBatches):
    sampleTimes = []

    for _ in range(numBatches):
        start = time.perf_counter()
        _ = buffer.get_data(batchSize)
        end = time.perf_counter()
        sampleTimes.append(end - start)

    totalTime = sum(sampleTimes)
    avgTime = totalTime / len(sampleTimes)
    if totalTime > 0:
        samplesPerSec = numBatches / totalTime
    else:
        samplesPerSec = 0
    
    return {
        "Total time": totalTime,
        "Average Time": avgTime,
        "Sampler per second": samplesPerSec
    }


def benchmark_PER_update(buffer, batchSize, numBatches):
    updateTimes = []
    totalUpdates = 0

    for _ in range(numBatches):
        res = buffer.get_data(batchSize)
        if res[0] is None:
            continue

        inputs, targets, treeIndices, episodes = res

        start = time.perf_counter()
        buffer.update_priorities(treeIndices, episodes)
        end = time.perf_counter()

        updateTimes.append(end - start)
        totalUpdates += len(treeIndices)

    totalTime = sum(updateTimes)
    if updateTimes:
        avgTime = totalTime / len(updateTimes)
    else:
        avgTime = 0
    if totalTime > 0:
        updatesPerSec = totalUpdates / totalTime
    else:
        updatesPerSec = 0
    
    return {
        "Total time": totalTime,
        "Average time": avgTime,
        "Updates per Second": updatesPerSec
    }


loss_fn = tf.keras.losses.MeanSquaredError()
optimizer = tf.keras.optimizers.Adam()

@tf.function
def train_step(model, x, y):
    with tf.GradientTape() as tape:
        qValues = model(x, training=True)
        loss = loss_fn(y, qValues)
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss


maze = np.array([
    [ 1.,  0.,  1.,  1.,  1.,  1.,  1.,  1.],
    [ 1.,  0.,  1.,  1.,  1.,  0.,  1.,  1.],
    [ 1.,  1.,  1.,  1.,  0.,  1.,  0.,  1.],
    [ 1.,  1.,  1.,  0.,  1.,  1.,  1.,  1.],
    [ 1.,  1.,  0.,  1.,  1.,  1.,  1.,  1.],
    [ 1.,  1.,  1.,  0.,  1.,  0.,  0.,  0.],
    [ 1.,  1.,  1.,  0.,  1.,  1.,  1.,  1.],
    [ 1.,  1.,  1.,  1.,  0.,  1.,  1.,  1.]
])




def benchmark_qtrain(maze, replayBuffer, model, targetModel, numEpochs=200, batchSize=32, epsilon=0.1, target_update_freq=50):
    sampleTimes = []
    trainTimes = []
    updateTimes = []
    stepTimes = []

    qmaze = Qmaze(maze)
    envSize = qmaze.observe().shape[1]
    numActions = 4

    totalSteps = 0
    totalEpisodes = 0

    #warmup
    # TODO lookup why .astype?
    x = np.random.rand(batchSize, envSize).astype(np.float32)
    y = np.random.rand(batchSize, numActions).astype(np.float32)
    _ = train_step(model, x, y)

    totalStart = time.perf_counter()

    for epoch in range(numEpochs):
        qmaze.reset((0, 0))
        envState = qmaze.observe()
        gameOver = False

        while not gameOver:
            stepStart = time.perf_counter()

            prevState = envState

            # epsilon-greedy action
            if np.random.rand() < epsilon:
                action = random.randint(0, numActions - 1)
            else:
                qVals = replayBuffer.predict(prevState)
                action = int(np.argmax(qVals))

            envState, reward, gameStatus = qmaze.act(action)
            gameOver = (gameStatus != 'not_over')

            episode = [prevState, action, reward, envState, gameOver]
            replayBuffer.remember(episode)

            sampleStart = time.perf_counter()
            batch = replayBuffer.get_data(batchSize)
            sampleEnd = time.perf_counter()
            sampleTimes.append(sampleEnd - sampleStart)

            if batch[0] is not None:
                if len(batch) == 2:
                    x, y = batch
                    batchIndices = None
                    batchEpisodes = None
                else:
                    x, y, batchIndices, batchEpisodes = batch
                
                trainStart = time.perf_counter()
                _ = train_step(model, x, y)
                trainEnd = time.perf_counter()
                trainTimes.append(trainEnd - trainStart)

                if batchIndices is not None:
                    updateStart = time.perf_counter()
                    replayBuffer.update_priorities(batchIndices, batchEpisodes)
                    updateEnd = time.perf_counter()
                    updateTimes.append(updateEnd - updateStart)

            stepEnd = time.perf_counter()
            stepTimes.append(stepEnd - stepStart)
            totalSteps += 1

        totalEpisodes += 1

        if epoch % target_update_freq == 0:
            targetModel.set_weights(model.get_weights())

    totalEnd = time.perf_counter()
    totalTime = totalEnd - totalStart

    return {
        "Episodes": totalEpisodes,
        "Steps": totalSteps,
        "Total Time": totalTime,
        "Average Sample Time": sum(sampleTimes) / len(sampleTimes) if sampleTimes else 0,
        "Average Train Time": sum(trainTimes) / len(trainTimes) if trainTimes else 0,
        "Average Update Time": sum(updateTimes) / len(updateTimes) if updateTimes else 0,
        "Steps per Second": totalSteps / totalTime if totalTime > 0 else 0
    }
