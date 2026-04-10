## this file controls the experience replay class
import numpy as np

class Experience(object):
    def __init__(self, model, targetModel, maxMemory = 100, discount = 0.95):
        self.model = model
        self.targetModel = targetModel
        self.maxMemory = maxMemory
        self.discount = discount
        self.memory = []
        self.numActions = model.output_shape[-1]

    def remember(self, episode):
        self.memory.append(episode)
        if len(self.memory) > self.maxMemory:
            del self.memory[0]

    def predict(self, envState):
        return self.model.predict(envState)[0]
    
    def get_data(self, dataSize=10):
        envSize = self.memory[0][0].shape[1]
        memSize = len(self.memory)
        dataSize = min(memSize, dataSize)
        inputs = np.zeros((dataSize, envSize))
        targets = np.zeros((dataSize, self.numActions))

        for i, j in enumerate(np.random.choice(range(memSize), dataSize, replace=False)):
            envState, action, reward, envStateNext, gameOver = self.memory[j]
            # lookup
            inputs[i] = envState[0]
            # lookup
            targets[i] = self.model.predict(envState)

            if gameOver:
                targets[i, action] = reward
            else:
                q_sa = np.max(self.targetModel.predict(envStateNext)[0])
                targets[i, action] = reward + self.discount * q_sa
            
        return inputs, targets
    