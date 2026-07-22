#!/usr/bin/env python3
import math
import random

import rospy
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
from geometry_msgs.msg import Quaternion
from std_srvs.srv import Empty, EmptyResponse
from tf.transformations import quaternion_from_euler


class EpisodeResetter:
    def __init__(self):
        rospy.init_node("episode_resetter")

        self.robot_model_name = rospy.get_param("~robot_model_name", rospy.get_param("robot_model_name", "group34Bot"))
        self.start_x = float(rospy.get_param("~start_x", rospy.get_param("start_x", 0.0)))
        self.start_y = float(rospy.get_param("~start_y", rospy.get_param("start_y", 0.0)))
        self.start_z = float(rospy.get_param("~start_z", rospy.get_param("start_z", 0.05)))
        self.start_yaw = float(rospy.get_param("~start_yaw", rospy.get_param("start_yaw", 0.0)))

        self.randomize_positions = bool(rospy.get_param("~randomize_positions", rospy.get_param("randomize_positions", False)))
        self.waypoints = rospy.get_param("~waypoints", rospy.get_param("waypoints", []))

        self.service_name = rospy.get_param("~service_name", "/group34Bot/reset_episode")

        rospy.wait_for_service("/gazebo/set_model_state")
        self.set_model_state = rospy.ServiceProxy("/gazebo/set_model_state", SetModelState)
        self.service = rospy.Service(self.service_name, Empty, self.handle_reset)
        rospy.loginfo("Episode reset service ready: %s (randomize=%s, waypoints=%d)",
                      self.service_name, self.randomize_positions, len(self.waypoints))

    def pick_start_pose(self):
        if self.randomize_positions and self.waypoints:
            wp = random.choice(self.waypoints)
            return float(wp["x"]), float(wp["y"]), self.start_z, float(wp.get("yaw", 0.0))
        return self.start_x, self.start_y, self.start_z, self.start_yaw

    def handle_reset(self, _request):
        x, y, z, yaw = self.pick_start_pose()

        state = ModelState()
        state.model_name = self.robot_model_name
        state.reference_frame = "world"
        state.pose.position.x = x
        state.pose.position.y = y
        state.pose.position.z = z

        q = quaternion_from_euler(0.0, 0.0, yaw)
        state.pose.orientation = Quaternion(q[0], q[1], q[2], q[3])

        state.twist.linear.x = 0.0
        state.twist.linear.y = 0.0
        state.twist.linear.z = 0.0
        state.twist.angular.x = 0.0
        state.twist.angular.y = 0.0
        state.twist.angular.z = 0.0

        try:
            response = self.set_model_state(state)
            if not response.success:
                rospy.logwarn("Gazebo reset failed: %s", response.status_message)
        except Exception as exc:
            rospy.logerr("Could not reset robot: %s", exc)

        return EmptyResponse()


if __name__ == "__main__":
    EpisodeResetter()
    rospy.spin()