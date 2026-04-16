# Artifact Selection for Enhancement #1 (Software Engineering & Design)
I plan on using a thermostat.py file artifact which leverages a raspberry pi 4 with a temperature & humidity sensor, leds, and buttons to relay state information via an LCD screen while also sending the state information (serially) to a server (a secondary script). This artifact originates from the CS 350 class.

## Plan Description
I plan on creating a secure device-to-server pipeline that implements device identification, secure transportation, authentication, replay protection, and secure storage of data. This plan incorporates separation of concerns, reliability, security, and maintainability as software engineering & design enhancements.

![Device-to-Server data transportation flow chart](https://github.com/Finnegan2024/Finnegan2024.github.io/blob/main/thermostat_device/Flowchart.png)

## Mapping Skills from Enahancement to Course Outcomes
This enhancement focuses on improving the quality of an existing code base, addressing limitations, and mitigating vulnerabilities to highlight my knowledge within embedded systems and cybersecurity.

This enhancement aligns with “Design, develop, and deliver professional-quality oral, written, and visual communications that are coherent, technically sound, and appropriately adapted to specific audiences and contexts” via documentation and diagrams to ensure all stakeholders understand the system. It also aligns with “Design and evaluate computing solutions that solve a given problem using algorithmic principles and computer science practices and standards appropriate to its solution, while managing the trade-offs involved in design choices” as I’ll be opting for HMAC-signed payloads instead of device certificates. This demonstrates my ability to assess tradeoffs such as ease of implementation vs very strong security for embedded systems. Another outcome this enhancement aligns with is “Demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals” as this enhancement is focused on leveraging HMAC-signed payloads, replay protection, TLS, and secret handling. Lastly, this enhancement aligns with “Develop a security mindset that anticipates adversarial exploits in software architecture and designs to expose potential vulnerabilities, mitigate design flaws, and ensure privacy and enhanced security of data and resources” as I’ll be focusing on strong security measures and real-world threats. 

# Artifact Selection for Enhancement #2 (Data Structures & Algorithms)
I plan on using a DQN .ipynb file artifact which leverages a neural network with 2 hidden layers to control an NPC. The goal of the assignment was to develop my own Q-training algorithm to find the best possible navigation sequence while maximizing reward to achieve a 100%-win rate. This artifact originates from the CS 370 class.

## Plan Description
I plan on enhancing my DQN using a prioritized experience replay implemented with a SumTree. The binary SumTree is a core data structure, and this enhancement will also demonstrate time complexity optimization by changing the replay buffer from a uniform O(N) to a prioritized replay buffer O(log N). This improves sampling speed and can be verified using benchmarks such as sampling time per batch, updates/sec, and steps/sec.

![DQN Flowchart](https://github.com/Finnegan2024/Finnegan2024.github.io/blob/main/DQN/DQN%20Flowchart.png)

## Mapping Skills from Enhancement to Course Outcomes
This enhancement focuses on optimization, time complexity, and throughput to highlight my knowledge within reinforcement learning algorithms.

This enhancement aligns with “Design, develop, and deliver professional-quality oral, written, and visual communications that are coherent, technically sound, and appropriately adapted to specific audiences and contexts” via documentation and diagrams to ensure all stakeholders understand the system. It also aligns with “Design and evaluate computing solutions that solve a given problem using algorithmic principles and computer science practices and standards appropriate to its solution, while managing the trade-offs involved in design choices” as I’ll be opting for a prioritized experience replay instead of a uniform replay buffer. This demonstrates my ability to assess tradeoffs such as ease of implementation vs faster sampling and lower memory overhead. Another outcome this enhancement aligns with is “Demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals” as this enhancement is focused on leveraging data structures with verifiable time complexity improvements.

# Artifact Selection for Enhancement #3 (Databases)
I plan on using a thermostat.py file artifact which leverages a raspberry pi 4 with a temperature & humidity sensor, leds, and buttons to relay state information via an LCD screen while also sending the state information (serially) to a server (a secondary script). This artifact originates from the CS 350 class.

## Plan Description
I plan on creating a secure device-to-server pipeline that implements device identification, secure transportation, authentication, replay protection, and secure storage of data. This plan incorporates schema designs, meaningful queries, constraints, and mitigations as database enhancements.

![Data Flow Diagram for Enhancement #3]()

## Mapping Skills from Enhancement to Course Outcomes
This enhancement focuses on improving the quality of an existing code base, addressing limitations, and mitigating vulnerabilities to highlight my knowledge within embedded systems and cybersecurity.

This enhancement aligns with “Design, develop, and deliver professional-quality oral, written, and visual communications that are coherent, technically sound, and appropriately adapted to specific audiences and contexts” via documentation and diagrams to ensure all stakeholders understand the system. It also aligns with “Design and evaluate computing solutions that solve a given problem using algorithmic principles and computer science practices and standards appropriate to its solution, while managing the trade-offs involved in design choices” as I’ll be opting for a HMAC-signed payloads instead of device certificates. This demonstrates my ability to assess tradeoffs such as ease of implementation vs very strong security for embedded systems. Another outcome this enhancement aligns to is “Demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals” as this enhancement is focused leveraging HMAC-signed payloads, replay protection, TLS, and secret handling. Lastly, this enhancement aligns with “Develop a security mindset that anticipates adversarial exploits in software architecture and designs to expose potential vulnerabilities, mitigate design flaws, and ensure privacy and enhanced security of data and resources” as I’ll be focusing on strong security measures and real-world threats. 
