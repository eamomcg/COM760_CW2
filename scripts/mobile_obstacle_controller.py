#!/usr/bin/env python3
"""
Workstream B: moves a simple Gazebo model back and forth to act as a dynamic obstacle.

The world file includes a model named moving_pedestrian. This script moves it
between two configured points using /gazebo/set_model_state.
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

        self.model_name = rospy.get_param("~model_name", "moving_pedestrian")
        self.x1 = float(rospy.get_param("~x1", 2.0))
        self.y1 = float(rospy.get_param("~y1", -1.0))
        self.x2 = float(rospy.get_param("~x2", 2.0))
        self.y2 = float(rospy.get_param("~y2", 2.5))
        self.z = float(rospy.get_param("~z", 0.50))
        self.speed = float(rospy.get_param("~speed", 0.35))
        self.rate_hz = float(rospy.get_param("~rate_hz", 20.0))

        self.current_x = self.x1
        self.current_y = self.y1
        self.target_x = self.x2
        self.target_y = self.y2

        rospy.wait_for_service("/gazebo/set_model_state")
        self.set_model_state = rospy.ServiceProxy("/gazebo/set_model_state", SetModelState)

    def swap_target_if_needed(self):
        distance = math.sqrt((self.target_x - self.current_x) ** 2 + (self.target_y - self.current_y) ** 2)
        if distance < 0.05:
            if self.target_x == self.x2 and self.target_y == self.y2:
                self.target_x, self.target_y = self.x1, self.y1
            else:
                self.target_x, self.target_y = self.x2, self.y2

    def step(self, dt):
        self.swap_target_if_needed()

        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance <= 0.001:
            return

        travel = min(self.speed * dt, distance)
        self.current_x += (dx / distance) * travel
        self.current_y += (dy / distance) * travel

        yaw = math.atan2(dy, dx)
        q = quaternion_from_euler(0.0, 0.0, yaw)

        state = ModelState()
        state.model_name = self.model_name
        state.reference_frame = "world"
        state.pose.position.x = self.current_x
        state.pose.position.y = self.current_y
        state.pose.position.z = self.z
        state.pose.orientation = Quaternion(q[0], q[1], q[2], q[3])
        self.set_model_state(state)

    def run(self):
        rate = rospy.Rate(self.rate_hz)
        last_time = rospy.Time.now()
        while not rospy.is_shutdown():
            now = rospy.Time.now()
            dt = max((now - last_time).to_sec(), 1.0 / self.rate_hz)
            last_time = now
            try:
                self.step(dt)
            except Exception as exc:
                rospy.logwarn_throttle(2.0, "Could not move mobile obstacle: %s", exc)
            rate.sleep()


if __name__ == "__main__":
    MobileObstacleController().run()
