# COM760 Coursework 2: Autonomous Robot Navigation

**Project Title:** Q-learning Based Autonomous Delivery Robot Navigation in a Simulated City Environment  
**Client Profile:** All Direct Furniture Ltd (Furniture Retailer, Belfast)  
**Module:** COM760 (Robotics & AI) MSc Assignment — Group 34 (Eamonn & John)

## Project Overview
This project designs and implements an autonomous navigation solution for a mobile delivery robot (`group34Bot`) operated by **All Direct Furniture Ltd**. The robot is trained to navigate a simulated city environment to automate urban furniture dispatches. The framework utilizes Python, ROS Noetic/Kinetic, and a tabular Q-learning reinforcement learning model to safely avoid static structures and mobile obstacles common in downtown Belfast delivery routes.

## Group 34 Members
* Eamonn McGurk - B00992264
* John O'Doherty - B00

## Branching Strategy & Workflow

This project utilizes the **GitHub Flow** strategy to maintain a stable codebase for collaboration:

* **`main` Branch:** Represents the production-ready state. Code on this branch must always compile successfully (`catkin_make`) and run without crashing. Direct commits to `main` are prohibited.
* **Feature Branches (`feature/feature-name`):** All development must take place on short-lived branches isolated by task (e.g., `feature/bug-logic`, `feature/custom-srv`). 
* **Integration:** Once a feature is implemented and tested locally, a Pull Request (PR) must be opened for review before merging back into `main`.
---

## Package Directory Structure
```text
com760cw2_group34/
├── CMakeLists.txt      # Catkin compilation configurations
├── package.xml         # Package node dependencies
├── launch/             # ROS launch scripts
├── msg/                # Custom ROS message definitions
├── scripts/            # Python source nodes & utilities
├── srv/                # Custom ROS service definitions
├── urdf/               # Modified robot model files
├── world/              # Gazebo world description files
└── results/            # Saved Q-tables and training CSV logs



