cmake_minimum_required(VERSION 3.0.2)
project(com760cw2_groupid)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
  sensor_msgs
  nav_msgs
  gazebo_msgs
  std_srvs
  message_generation
  robot_state_publisher
)

add_message_files(
  FILES
  QLearningStatus.msg
)

add_service_files(
  FILES
  SetDeliveryGoal.srv
)

generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS
  rospy
  std_msgs
  geometry_msgs
  sensor_msgs
  nav_msgs
  gazebo_msgs
  std_srvs
  message_runtime
)

catkin_install_python(PROGRAMS
  scripts/q_learning_node.py
  scripts/state_encoder.py
  scripts/action_executor.py
  scripts/reward_manager.py
  scripts/training_logger.py
  scripts/reset_episode.py
  scripts/mobile_obstacle_controller.py
  scripts/plot_results.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
