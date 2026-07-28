#!/usr/bin/env python3
"""
Workstream B: moves a simple Gazebo model back and forth to act as a dynamic obstacle.
The world file includes a model named moving_pedestrian.
This script moves it between two configured points using /gazebo/set_model_state.
"""

import math
import rospy
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
from geometry_msgs.msg import Quaternion
from tf.transformations import quaternion_from_euler

class MobileObstacleController:
    def __init__(self):
        rospy.init_node("mobile_obstacle_controller")
        
        # Wait for the Gazebo service to become available before proceeding
        rospy.loginfo("Waiting for /gazebo/set_model_state service...")
        rospy.wait_for_service('/gazebo/set_model_state')
        self.set_state_srv = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)
        
        self.model_name = "moving_pedestrian"
        self.rate = rospy.Rate(10) # Update the position at 10 Hz
        
        # Movement parameters based on your world file's initial pose (4.0, -2.4, 0.50)
        self.base_x = 4.0
        self.base_y = -2.4
        self.amplitude = 2.5     # How far it moves along the Y-axis (meters)
        self.frequency = 0.4     # How fast it oscillates

    def run(self):
        rospy.loginfo(f"Starting movement for {self.model_name}...")
        start_time = rospy.get_time()
        
        while not rospy.is_shutdown():
            current_time = rospy.get_time()
            elapsed = current_time - start_time
            
            # Calculate new Y position using a sine wave for smooth back-and-forth motion
            new_y = self.base_y + self.amplitude * math.sin(self.frequency * elapsed)
            
            # Construct the ModelState message
            state_msg = ModelState()
            state_msg.model_name = self.model_name
            
            # Set the new position
            state_msg.pose.position.x = self.base_x
            state_msg.pose.position.y = new_y
            state_msg.pose.position.z = 0.50 # Keep it at the height defined in the world file
            
            # Keep orientation static (facing forward)
            q = quaternion_from_euler(0, 0, 0)
            state_msg.pose.orientation = Quaternion(*q)
            
            # Send the service request to Gazebo
            try:
                self.set_state_srv(state_msg)
            except rospy.ServiceException as e:
                rospy.logerr(f"Gazebo SetModelState service call failed: {e}")
                
            self.rate.sleep()

if __name__ == "__main__":
    try:
        MobileObstacleController().run()
    except rospy.ROSInterruptException:
        pass