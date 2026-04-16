---
layout: post
title: "CS 499 Existing Code Base Review"
date: 2026-04-02
categories: [CODE-REVIEW]
---

# Code Review: Deep Q-Network & Raspberry Pi State Machine

[**Video Walkthrough:**](https://youtu.be/gEPCJszszJg)

[**Repository:**](https://github.com/Finnegan2024/Finnegan2024.github.io)

## Overview

This post documents a review of a Deep Q-Network & a Raspberry Pi State Machine, including its current architecture, implementation decisions, technical weaknesses, and the improvements I plan to make next.

The goal of the review was simple: understand the system as is, identify what is working, identify what needs improved, and define a clear path toward a stronger version of the project.

## What the Projects Do

## Deep Q-Network

This project is a Deep Q-Network (DQN) implementation that trains an agent to solve a treasure-hunt maze by learning which moves lead it to the goal. The system combines a custom maze environment, neural network-based decision making, and a training loop that uses experience replay and exploration to improve performance over time. It demonstrates how reinforcement learning can be applied to a grid-based pathfinding problem while also showing the relationship between environment design, reward logic, and model behavior. I selected this artifact because it provides a strong foundation for discussing both the current implementation and future improvements in structure, efficiency, and scalability.

## Raspberry Pi State Machine

This project is a Raspberry Pi–based thermostat implemented as a finite state machine that cycles between off, heat, and cool modes in response to button input. It integrates hardware components including temperature sensing, LED indicators, an LCD display, and serial communication to create a working embedded system that both reacts to environmental conditions and reports its status outward. The artifact demonstrates how software logic, hardware control, and state-based design can work together in a real device rather than a purely simulated environment. I selected this project because it provides a strong foundation for discussing system design, hardware-software interaction, and future enhancements in reliability, security, and data handling.

## What I Reviewed

During the review, I focused on:

- overall structure and separation of concerns
- readability and maintainability
- algorithmic efficiency
- data handling and persistence
- validation, reliability, and edge cases
This review is the baseline for the next version of the project.
