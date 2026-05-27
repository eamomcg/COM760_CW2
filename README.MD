# COM760 Coursework 2: Autonomous Robot Navigation

## Project Overview
This project is developed by Group 34 (Eamonn McGurk and John O'Doherty) for the COM760 (Robotics & AI) MSc module and Coursework 2 brief. The objective is to design and develop an autonomous navigation solution for a mobile robot operating within the Gazebo simulator environment

## Objectives
* **Autonomous Navigation:** Program a mobile robot to navigate an unknown environment safely using Python and ROS[cite: 14, 16, 17, 23]. This is achieved by implementing local sensor-based logic (Bug algorithms) or a machine learning approach (Q-Learning)
* **Custom ROS Communications:** Implement custom ROS services and messages to actively control the robot's behaviors, travel speed, and turning direction upon obstacle contact
* **Socio-Ethical Evaluation:** Critically evaluate the broader real-world implications of deploying this robotics solution, focusing on safety, privacy, algorithmic bias, and sustainability

## Group 34 Members
* Eamonn McGurk - B00992264
* John O'Doherty - B00

## Branching Strategy & Workflow

This project utilizes the **GitHub Flow** strategy to maintain a stable codebase for collaboration:

* **`main` Branch:** Represents the production-ready state. Code on this branch must always compile successfully (`catkin_make`) and run without crashing. Direct commits to `main` are prohibited.
* **Feature Branches (`feature/feature-name`):** All development must take place on short-lived branches isolated by task (e.g., `feature/bug-logic`, `feature/custom-srv`). 
* **Integration:** Once a feature is implemented and tested locally, a Pull Request (PR) must be opened for review before merging back into `main`.
