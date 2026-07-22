# Workstream Steps

## Workstream A: Q-learning logic

1. Check `q_learning_node.py` launches and receives `/group34Bot/laser/scan` and `/odom`.
2. Check `state_encoder.py` prints sensible state keys when the robot faces obstacles.
3. Check `action_executor.py` moves the robot for each action ID.
4. Check `reward_manager.py` gives positive rewards for progress and terminal reward at the goal.
5. Run random behaviour using high epsilon.
6. Train in the static world first.
7. Save the Q-table and inspect `results/q_table.json`.
8. Run demo mode with epsilon set to zero.
9. Produce reward and success-rate graphs from the CSV logs.

## Workstream B: Gazebo/CitySim world and robot setup

1. Launch `world_only.launch` and confirm Gazebo opens.
2. Confirm the robot spawns as `group34Bot`.
3. Confirm `/group34Bot/cmd_vel` moves the robot.
4. Confirm `/group34Bot/laser/scan` publishes laser data.
5. Confirm `/odom` publishes odometry.
6. Confirm the static buildings/barriers are detected by the laser.
7. Confirm `moving_pedestrian` exists in Gazebo.
8. Run `mobile_obstacle_controller.py` and confirm the obstacle moves.
9. Run `reset_episode.py` and confirm the robot resets to the start pose.
10. Improve the city world layout once the AI loop works.

## Shared integration

1. Build the custom message and service with `catkin_make`.
2. Test `rosmsg show com760cw2_group34/QLearningStatus`.
3. Test `rossrv show com760cw2_group34/SetDeliveryGoal`.
4. Run `train_q_learning.launch`.
5. Fix topic mismatches first; tune learning only after topics are correct.
6. Record baseline random policy.
7. Record trained policy in static obstacles.
8. Record trained policy with mobile obstacle.
9. Use logs and screenshots in the final report.
