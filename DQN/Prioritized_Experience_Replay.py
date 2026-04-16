## this file controls the experience replay class which leverages a SumTree to improve time complexity of experience sampling
## The following resources aided me in my implementation of the SumTree data structure and priorizited experience replay
## https://github.com/rlcode/per/blob/master/prioritized_memory.py
## https://github.com/rlcode/per/blob/master/SumTree.py

import numpy as np
import random

class PER(object):
    def __init__(self, model, targetModel, maxMemory = 100, discount = 0.95):
        self.model = model
        self.targetModel = targetModel
        self.maxMemory = maxMemory
        self.discount = discount
        self.memory = SumTree(self.maxMemory)
        self.numActions = model.output_shape[-1]

    # Change #3, calculate tderror and priority before adding episode alongside priority in SumTree
    def remember(self, episode):
        tdError = self.get_td_error(episode)
        priority = self.getPriority(tdError)
        self.memory.add_node(priority, episode)

    def predict(self, envState):
        return self.model.predict(envState)[0]
    
    def get_data(self, dataSize=10):
        envSize = self.memory[0][0].shape[1]
        memSize = self.memory.numEntries
        dataSize = min(memSize, dataSize)
        if dataSize == 0:
            return None, None, None, None
        
        inputs = np.zeros((dataSize, envSize))
        targets = np.zeros((dataSize, self.numActions))

        treeIndices = []
        sampledEpisodes = []

        # segment memory to reduce bias
        totalPriority = self.memory.get_total()
        segment = totalPriority / dataSize

        for i in range(dataSize):
            start = segment * i
            end = segment * (i + 1)
            val = np.random.uniform(start, end)

            treeIndx, priority, episode = self.memory.get_node(val)
            envState, action, reward, envStateNext, gameOver = self.memory[i]
            
            inputs[i] = envState[0]
            targets[i] = self.model.predict(envState)

            if gameOver:
                targets[i, action] = reward
            else:
                q_sa = np.max(self.targetModel.predict(envStateNext)[0])
                targets[i, action] = reward + self.discount * q_sa

            treeIndices.append(treeIndx)
            sampledEpisodes.append(episode)
        
        # Change #4, return treeIndices and sampledEpisodes to update memory priorities in the training function
        return inputs, targets, treeIndices, sampledEpisodes
    
    # Change #5, calculate td error to use in calculating priority
    def get_td_error(self, episode):
        envState, action, reward, envStateNext, gameOver = episode

        currQ = self.model.predict(envState)[0]
        q_sa = currQ[action]

        if gameOver:
            target = reward
        else:
            nextQ = self.targetModel.predict(envState)[0]
            target = reward + self.discount * np.max(nextQ)

        tdError = abs(target - q_sa)
        return tdError
    
    # Change #6, calculate priority for SumTree leaf nodes
    # epsilon avoids a zero priority so there is no experience bias
    # alpha controls how much priority matters in sampling
    def getPriority(self, error,  epsilon=0.01, alpha=0.8):
        return (error + epsilon) ** alpha
    

    #Change #7, helper method to update priorities in memory
    def update_priorities(self, treeIndices, episodes):
        for indx, episode in zip(treeIndices, episodes):
            err = self.get_td_error(episode)
            priority = self.getPriority(err)
            self.memory.update(indx, priority)
    

# Change #8
# leverage a sumtree data structure to improve time complexity of experience replay from O(N) to O(log N) and holded priority values
class SumTree:
    def __init__(self, capacity):
        self.capacity = capacity
        # tree holds nodes
        self.tree = np.zeros(2 * capacity - 1)
        # data holds values
        self.data = np.zeros(capacity, dtype=object)
        self.numEntries = 0
        self.currNode = 0

    # since the parent node is the total of right & left child, we need to propogate changes up the tree when changing the weights of the leaf nodes
    # leaf nodes hold the weight of each transition allowing us to sample the more important transitions more often.
    def propagate(self, indx, change):
        while indx != 0:
            node = (indx - 1) // 2
            self.tree[node] += change

    
    # Returns sampled experience
    def get_sample(self, indx, value):
        left = 2 * indx + 1
        right = left + 1

        if left >= len(self.tree):
            return indx
        
        if value <= self.tree[left]:
            return self.get_sample(left, value)
        else:
            return self.get_sample(right, value - self.tree[left])
        

    # Cumulative sum of tree
    def get_total(self):
        return self.tree[0]
    

    def add_node(self, priority, value):
        indx = self.currNode + self.capacity - 1

        self.data[self.currNode] = value
        self.update(indx, priority)

        self.currNode += 1
        if self.currNode >= self.capacity:
            self.currNode = 0
        
        if self.numEntries < self.capacity:
            self.numEntries += 1

    # Update priority
    def update(self, indx, priority):
        # ensure update only happens on leaf nodes
        if indx < self.capacity - 1 or indx >= len(self.tree):
            raise IndexError("Update must start from a valid leaf node")
        

        difference = priority - self.tree[indx]

        self.tree[indx] = priority
        self.propagate(indx, difference)

    # Returns priority and sample
    def get_node(self, value):
        index = self.get_sample(0, value)
        dataIndx = index - self.capacity + 1

        return (index, self.tree[index], self.data[dataIndx])
    
