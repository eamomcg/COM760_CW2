# COM760 Coursework 2: Autonomous Robot Navigation

**Project Title:** Q-learning Based Autonomous Delivery Robot Navigation in a Simulated City Environment  
**Module:** COM760 (Robotics & AI) MSc Assignment — Group 34 (Eamonn & John)

## Project Overview
last mile delivery robot service in urban area

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



