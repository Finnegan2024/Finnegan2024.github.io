from __future__ import print_function
import os, sys, time, datetime, json, random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import clone_model
from keras.models import Sequential
from keras.layers import Dense, Activation, PReLU
from keras.optimizers import SGD , Adam, RMSprop
import matplotlib.pyplot as plt
from Prioritized_Experience_Replay import PER
import Qmaze
# %matplotlib inline



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



def show(qmaze):
    plt.grid('on')
    nrows, ncols = qmaze.maze.shape
    ax = plt.gca()
    ax.set_xticks(np.arange(0.5, nrows, 1))
    ax.set_yticks(np.arange(0.5, ncols, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    canvas = np.copy(qmaze.maze)
    for row,col in qmaze.visited:
        canvas[row,col] = 0.6
    pirate_row, pirate_col, _ = qmaze.state
    canvas[pirate_row, pirate_col] = 0.3   # pirate cell
    canvas[nrows-1, ncols-1] = 0.9 # treasure cell
    img = plt.imshow(canvas, interpolation='none', cmap='gray')
    return img



LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3


# Exploration factor
epsilon = 1.0
epsilon_min = 0.05
epsilon_decay = 0.99
patience = 10

# Actions dictionary
actions_dict = {
    LEFT: 'left',
    UP: 'up',
    RIGHT: 'right',
    DOWN: 'down',
}

num_actions = len(actions_dict)



qmaze = Qmaze(maze)
canvas, reward, game_over = qmaze.act(DOWN)
print("reward=", reward)
show(qmaze)



def play_game(model, qmaze, pirate_cell, max_steps=None):
    qmaze.reset(pirate_cell)
    envstate = qmaze.observe()
    steps = 0
    if max_steps is None:
        max_steps = qmaze.maze.size * 4  # safety cutoff

    while steps < max_steps:
        state = np.asarray(envstate, dtype=np.float32)
        if state.ndim == 1:
            state = np.expand_dims(state, axis=0)

        q_values = model(state, training=False).numpy()
        action = np.argmax(q_values[0])

        envstate, reward, game_status = qmaze.act(action)
        steps += 1

        if game_status == 'win':
            return True
        elif game_status == 'lose':
            return False

    return False  # timed out with no result



def completion_check(model, maze_or_qmaze, max_steps=None):
    # Accept either raw numpy maze or QMaze instance
    if isinstance(maze_or_qmaze, Qmaze):
        qmaze = maze_or_qmaze
    else:
        qmaze = Qmaze(maze_or_qmaze)

    for cell in qmaze.free_cells:
        if not qmaze.valid_actions(cell):
            continue
        if not play_game(model, qmaze, cell, max_steps=max_steps):
            return False
    return True



def build_model(maze):
    model = Sequential()
    model.add(Dense(maze.size, input_shape=(maze.size,)))
    model.add(PReLU())
    model.add(Dense(maze.size))
    model.add(PReLU())
    model.add(Dense(num_actions))
    model.compile(optimizer='adam', loss='mse')
    return model



loss_fn = tf.keras.losses.MeanSquaredError()
optimizer = tf.keras.optimizers.Adam()

@tf.function
def train_step(x, y):
    with tf.GradientTape() as tape:
        q_values = model(x, training=True)
        loss = loss_fn(y, q_values)
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss



def qtrain(model, maze, **opt):
    # exploration factor
    global epsilon 
    
    # Number of epochs
    n_epoch = opt.get('n_epoch', 15000)
    
    # Maximum meory to store episodes
    max_memory = opt.get('max_memory', 1000)
    
    # Maximum data size for training
    data_size = opt.get('data_size', 50)
    
    # Frequency of target network updates
    target_update_freq = opt.get('target_update_freq', 50)
    
    # Start time
    start_time = datetime.datetime.now()
    
    # Construct environment/game from numpy array: maze (see argument above)
    qmaze = Qmaze(maze)
    
    # Target Network to better guide training
    target_model = clone_model(model)
    target_model.set_weights(model.get_weights())
    
    # Initialize experience replay object
    experience = PER(model, target_model, max_memory=max_memory)

    win_history = [] # history of win/lose game
    hsize = qmaze.maze.size // 2 #history window size
    win_rate = 0.0

    n_episodes = 0
    
    # =============START_HERE================
    for epoch in range(n_epoch): 
        # ---- choose starting cell with a simple curriculum ----
        warmup_epochs = 300  # you can adjust this

        if epoch < warmup_epochs:
            # early training: always start from (0, 0)
            agent_cell = (0, 0)
        else:
            # later training: start from random free cell
            agent_cell = random.choice(qmaze.free_cells)
        # reset maze and get env state
        qmaze.reset(agent_cell)
        env_state = qmaze.observe()

        game_over = False
        loss = [] # track batch losses within epoch
        steps = 0

        while not game_over:
            steps += 1
            previous_envstate = env_state

            # Decide on action
            if np.random.rand() < epsilon:
                # Exploration bias
                action = random.randint(0, num_actions - 1)
            else:
                # exploitation bias
                q_values = experience.predict(previous_envstate)
                #best_valid = max(valid_actions, key=lambda a: q_values[a])
                action = int(np.argmax(q_values))

            # takes action in environment
            env_state, reward, game_status = qmaze.act(action)

            # track wins and losses
            if game_status == 'win':
                win_history.append(1)
                game_over = True
            elif game_status =='lose':
                win_history.append(0)
                game_over = True
            else:
                game_over = False

            # store transition in replay memory
            episode = [previous_envstate, action, reward, env_state, game_over]
            experience.remember(episode)

            # Change #1, use prioritized replay
            trainingInput, trainingTarget, batchIndices, batchEpisodes = experience.get_data(batch_size=data_size)
            if trainingInput is not None:
                batch_loss = train_step(trainingInput, trainingTarget)
                loss.append(float(batch_loss.numpy()))

            # Change #2, update sample priorities
            # after model updates, update sampled transitions
            experience.updatePriorities(batchIndices, batchEpisodes)

        n_episodes += 1

        # update target frequently
        if epoch % target_update_freq == 0:
            target_model.set_weights(model.get_weights())

        # computes avg loss
        epoch_loss = np.mean(loss) if loss else 0.0
        
        # Win rate over last hsize steps 
        win_rate = sum(win_history[-hsize:]) / hsize if len(win_history) >= hsize else 0.0

        # Print the epoch, loss, episode, win count, win rate, and time for each epoch
        dt = datetime.datetime.now() - start_time
        t = format_time(dt.total_seconds())
        print("Epoch: {:03d}/{:d} | Loss: {:.4f} | Episodes: {:d} | Win count: {:d} | Win rate: {:.3f} | time: {}".format(
            epoch, n_epoch-1, epoch_loss, n_episodes, sum(win_history), win_rate, t))

        # Check if training has exhausted all free cells and if in all
        # cases the agent won
        # ---------- EPSILON UPDATE ----------
        total_wins = sum(win_history)

        if total_wins == 0:
            # no win yet: keep exploring fully
            epsilon = 1.0
        else:
            # after at least one win, use the original schedule
            if win_rate > 0.9:
                epsilon = 0.05
            else:
                epsilon = max(epsilon * epsilon_decay, epsilon_min)
    
        if win_rate >= 0.999 and completion_check(model, maze):
            print(f"Reached 100% win rate at epoch {epoch}")
            break

    total_time = format_time((datetime.datetime.now() - start_time).total_seconds())
    print("Training complete in:", total_time)

    # ---------- 2b: run one greedy test episode ----------
    # (Optional debug; uses existing play_game/completion_check code)
    test_qmaze = Qmaze(maze)
    success = play_game(model, test_qmaze, pirate_cell=(0, 0))
    print("Greedy test from (0, 0) success:", success)


# This is a small utility for printing readable time strings:
def format_time(seconds):
    if seconds < 400:
        s = float(seconds)
        return "%.1f seconds" % (s,)
    elif seconds < 4000:
        m = seconds / 60.0
        return "%.2f minutes" % (m,)
    else:
        h = seconds / 3600.0
        return "%.2f hours" % (h,)



qmaze = Qmaze(maze)
show(qmaze)



model = build_model(maze)
qtrain(model, maze, n_epoch=1000, max_memory=8*maze.size, data_size=64, target_update_freq=50)



completion_check(model, qmaze)
show(qmaze)



pirate_start = (0, 0)
play_game(model, qmaze, pirate_start)
show(qmaze)



