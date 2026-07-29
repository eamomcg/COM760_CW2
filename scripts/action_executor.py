#!/usr/bin/env python3

from geometry_msgs.msg import Twist


class ActionExecutor:
    def __init__(self, linear_speed=0.20, angular_speed=0.65):
        self.linear_speed = linear_speed
        self.angular_speed = angular_speed

        # action_id: (description, linear.x, angular.z)
        self.actions = {
            0: ("forward", linear_speed, 0.0),
            1: ("turn_left", 0.0, angular_speed),
            2: ("turn_right", 0.0, -angular_speed),
            3: ("forward_left", linear_speed * 0.70, angular_speed * 0.45),
            4: ("forward_right", linear_speed * 0.70, -angular_speed * 0.45),
            5: ("stop", 0.0, 0.0),
        }

    @property
    def action_count(self):
        return len(self.actions)

    def get_action_name(self, action_id):
        return self.actions.get(action_id, ("unknown", 0.0, 0.0))[0]

    def get_twist(self, action_id):
        if action_id not in self.actions:
            action_id = 5

        _, linear_x, angular_z = self.actions[action_id]
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        return msg

    def stop_twist(self):
        return self.get_twist(5)
