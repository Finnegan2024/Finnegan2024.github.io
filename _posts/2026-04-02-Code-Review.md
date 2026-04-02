---
layout: post
title: "CS 499 Existing Code Base Review"
date: 2026-04-02
categories: [CODE-REVIEW]
---

# Code Review: Deep Q-Network & Raspberry Pi State Machine

**Video Walkthrough:** https://youtu.be/gEPCJszszJg
**Repository:** https://github.com/Finnegan2024/Finnegan2024.github.io

## Overview

This post documents a review of a Deep Q-Network & a Raspberry Pi State Machine, including its current architecture, implementation decisions, technical weaknesses, and the improvements I plan to make next.

The goal of the review was simple: understand the system as it exists today, identify what is working, identify what is fragile, and define a clear path toward a stronger version of the project.

## What the Projects Do

## Deep Q-Network

This project is a Deep Q-Network (DQN) implementation that trains an agent to solve a treasure-hunt maze by learning which moves lead it to the goal. The system combines a custom maze environment, neural network-based decision making, and a training loop that uses experience replay and exploration to improve performance over time. It demonstrates how reinforcement learning can be applied to a grid-based pathfinding problem while also showing the relationship between environment design, reward logic, and model behavior. I selected this artifact because it provides a strong foundation for discussing both the current implementation and future improvements in structure, efficiency, and scalability.

## Raspberry Pi State Machine

This project is a Raspberry Pi–based thermostat implemented as a finite state machine that cycles between off, heat, and cool modes in response to button input. It integrates hardware components including temperature sensing, LED indicators, an LCD display, and serial communication to create a working embedded system that both reacts to environmental conditions and reports its status outward. The artifact demonstrates how software logic, hardware control, and state-based design can work together in a real device rather than a purely simulated environment. I selected this project because it provides a strong foundation for discussing system design, hardware-software interaction, and future enhancements in reliability, security, and data handling.

## What I Reviewed

During the review, I focused on the parts of the project that matter most in a real engineering setting:

- overall structure and separation of concerns
- readability and maintainability
- algorithmic efficiency
- data handling and persistence
- validation, reliability, and edge cases

## Key Findings

### What’s working

## Deep Q-Network
- The project successfully defines a custom maze environment where the agent can interact with the grid, receive rewards, and attempt to reach the goal.
- The neural network, training loop, and exploration logic are all connected well enough to let the agent learn through repeated episodes.
- The artifact already demonstrates the core reinforcement learning pipeline, including state observation, action selection, reward processing, and experience replay.

## Raspberry Pi State Machine
- The thermostat state machine correctly supports the three main operating states: off, heat, and cool.
- The hardware integration is functional, with buttons triggering state and setpoint changes while the LEDs and LCD provide live feedback.
- The system also sends periodic status updates over serial communication, showing that the thermostat logic and external reporting are already connected.

### What needs improvement

## Deep Q-Network
- The project is not very modular yet, since environment logic, model setup, training behavior, and evaluation are closely packed together instead of being separated more cleanly
- The current implementation could do a better job tracking performance with clearer benchmarking, comparison metrics, and testing across training runs.
- The replay and training strategy can be improved for efficiency and scalability, especially if the goal is to compare standard replay against stronger approaches like prioritized experience replay.

## Raspberry Pi State Machine
- The thermostat code is tightly coupled to the hardware and runtime flow, which makes it harder to test, maintain, or extend without refactoring.
- Input validation, error handling, and defensive programming around sensor reads, serial communication, and external failures could be stronger.
- The data reporting approach is basic and would benefit from more structured, secure, and reliable handling if the system is expanded beyond a simple prototype.

## Engineering Takeaways

The biggest takeaway from this review is that working code is only the baseline. A stronger implementation needs to be easier to read, easier to maintain, safer around bad input, and more deliberate in how it handles data and structure.

This review helped me identify where the current version behaves like a class project and where it needs to evolve toward production-minded engineering.

## Next Steps

Based on the review, my next improvements will focus on:

- refactoring for cleaner structure
- improving reliability and defensive programming
- strengthening the algorithmic side of the implementation
- improving persistence and data handling
- making the project easier to extend and maintain

## Why This Review Matters

I see code review as one of the most important engineering habits. It forces a project to be evaluated beyond “it runs” and pushes the work toward stronger design decisions, clearer tradeoffs, and better long-term quality.

This review is the baseline for the next version of the project.
