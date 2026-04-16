---
layout: post
title: "Enhancement #2: Deep Q-Network with Prioritized Experience Replay"
date: 2026-04-10
categories: [DATA-STRUCTURES, ALGORITHMS, DEEP-Q-NETWORK]
author: Finnegan Thomas
---
{{ post.author }}

**Repository:** [DQN](https://github.com/Finnegan2024/Finnegan2024.github.io/tree/main/DQN)

## Overview

This enhancement replaces the DQN's uniform experience replay buffer with **Prioritized Experience Replay (PER)** utilizing a **SumTree data structure**. The objective is to improve **sampling time complexity** from O(N) to O(log N). End-to-end training throughput involves separate trade-offs. For example, per-sample `predict()` is consciously left out of scope. The focus here is on the algorithmic and structural improvement to the sampling mechanism itself.

Prioritization is foucsed on transitions with higher **temporal-difference (TD) error** which represents the largest gap between the model's prediction and observed outcome. These are the most informative transitions for learning. Sampling uniformly ignores this signal entirely. Sampling proportionally to TD error turns the replay buffer from passive storage into an active part of the training loop.

## Design Decisions and Trade-offs

Before implementation, several design choices required deliberate trade-offs.

**Priority scaling (`alpha`).** The priority of a transition is computed as:

```python
def getPriority(self, error, epsilon=0.01, alpha=0.8):
    return (error + epsilon) ** alpha
```

At `alpha=1.0`, sampling is fully proportional to error causing high-priority transitions to dominate. At `alpha=0.0`, sampling reverts back to uniform. The chosen value of `0.8` is a middle ground for meaningful prioritization without completely avoiding low-error transitions that may still carry useful signal.

**Priority floor (`epsilon`).**  `epsilon=0.01` ensures no transition ever reaches zero priority. Without it, experiences the model has learned well would never be revisited which could hurt the model's training by forming irreversible sampling bias.

**Stratified sampling over greedy sampling.** Rather than always pulling the highest-priority transitions, `get_data()` divides the total priority range into equal segments and draws one sample per segment:

```python
totalPriority = self.memory.get_total()
segment = totalPriority / dataSize
for i in range(dataSize):
    val = np.random.uniform(segment * i, segment * (i + 1))
    treeIndx, priority, episode = self.memory.get_node(val)
```

Purely greedy sampling would cause the same small set of high-error transitions to dominate every batch, causing training instability. Stratified sampling preserves priority by diversifying across each batch.

**Insert cost vs. sample cost.** The SumTree increases insert cost slightly from O(1) to O(log N) compared to a naive array buffer. This is an accepted trade-off: inserts happen once per transition, while sampling happens every training step across the full batch size. Optimizing the more frequent, more expensive operation is beneficial to overall training.

## SumTree: The Algorithmic Core

A naive priority buffer requires O(N) to scane. The SumTree solves this by maintaining a binary tree where each internal node holds the **sum of its children's priorities**, making the root always equal to total priority in O(1).

**Sampling** traverses the tree top-down in O(log N), branching based on whether a random value falls within the left or right subtree's cumulative sum:

```python
def get_sample(self, indx, value):
    left = 2 * indx + 1
    right = left + 1
    if left >= len(self.tree):
        return indx
    if value <= self.tree[left]:
        return self.get_sample(left, value)
    else:
        return self.get_sample(right, value - self.tree[left])
```

**Priority updates** propagate upward from the modified leaf to the root in O(log N):

```python
def propagate(self, indx, change):
    while indx != 0:
        node = (indx - 1) // 2
        self.tree[node] += change
        indx = node
```

| Operation | Naive Buffer | SumTree |
|---|---|---|
| Insert | O(1) | O(log N) |
| Sample one transition | O(N) | O(log N) |
| Update priority | O(N log N) | O(log N) |

A full batch of `data_size` transitions drops from O(N × data_size) to O(log N × data_size).

After each gradient update, the priorities of sampled transitions are recalculated against the updated model weights:

```python
# new_DQN.py — training loop
trainingInput, trainingTarget, batchIndices, batchEpisodes = experience.get_data(batch_size=data_size)
if trainingInput is not None:
    batch_loss = train_step(trainingInput, trainingTarget)
    loss.append(float(batch_loss.numpy()))

experience.updatePriorities(batchIndices, batchEpisodes)
```

This is what makes the system self-correcting. As the model improves on a transition, its TD error shrinks and its priority declines. New or still-difficult transitions rise to the top without any manual intervention. The buffer continuously reflects the current state of the model's knowledge.

## Reflection

The uniform buffer was unaware of each transition's learning value. The move to PER considered the *properties* of the data being stored, not just the mechanics of storing it: what makes one transition more valuable than another, how to quantify that, and how to build a structure that exploits it efficiently.

Selecting the SumTree reduced the sampling bottleneck.
