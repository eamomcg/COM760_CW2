#!/usr/bin/env python3
"""
Workstream A: converts raw ROS sensor/odometry information into a small
Q-learning state.

The Q-table should not use raw LaserScan arrays directly. This file reduces the
scan to a few human-readable obstacle sectors and combines them with the goal
angle/distance.

FIX (see reward_manager.py for the matching fix): a LaserScan value that is
NaN/Inf means "no return" -> nothing detected -> treat as clear (max_range).
A value that is 0.0 or below the sensor's own range_min means the sensor is
saturated at its floor -> the obstacle is at or inside the minimum measurable
distance -> treat as VERY CLOSE (range_min), never as clear. The previous
version collapsed both cases to max_range, which silently erased genuine
near-collision readings.
"""

import math
import hashlib


class StateEncoder:
    def __init__(self,
                 blocked_distance=0.45,
                 near_distance=1.00,
                 goal_close_distance=0.60,
                 goal_medium_distance=2.50,
                 goal_far_distance=8.00):
        self.blocked_distance = blocked_distance
        self.near_distance = near_distance
        self.goal_close_distance = goal_close_distance
        self.goal_medium_distance = goal_medium_distance
        self.goal_far_distance = goal_far_distance

        # Sectors are in degrees, relative to the laser frame.
        # Positive degrees usually point to the left side of the robot.
        self.sectors = {
            "front": (-20, 20),
            "front_left": (20, 60),
            "left": (60, 105),
            "front_right": (-60, -20),
            "right": (-105, -60),
        }

    @staticmethod
    def normalise_angle(angle):
        """Return angle in range [-pi, pi]."""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    @staticmethod
    def stable_state_id(state_key):
        """Stable integer ID for custom status messages/logs."""
        digest = hashlib.md5(state_key.encode("utf-8")).hexdigest()
        return int(digest[:8], 16) % 2147483647

    def _valid_range(self, value, max_range, range_min):
        """
        Sanitize a single LaserScan range reading.

        - None / NaN / Inf  -> no return -> nothing detected -> max_range (clear)
        - <= 0.0 or < range_min -> sensor saturated at its floor -> the
          obstacle is AT LEAST as close as range_min -> return range_min
          (near/contact), never max_range. This is the case that matters
          most: it is what a real collision or near-collision looks like.
        - otherwise -> clamp into [range_min, max_range]
        """
        if value is None:
            return max_range
        if math.isnan(value) or math.isinf(value):
            return max_range
        if value <= 0.0 or value < range_min:
            return range_min
        return min(value, max_range)

    def _sector_min(self, scan_msg, deg_min, deg_max):
        """Minimum laser distance inside a sector."""
        if scan_msg is None or not scan_msg.ranges:
            return float("inf")

        max_range = scan_msg.range_max if scan_msg.range_max > 0 else 10.0
        range_min = scan_msg.range_min if scan_msg.range_min > 0 else 0.05
        result = max_range

        for index, raw_value in enumerate(scan_msg.ranges):
            angle_rad = scan_msg.angle_min + (index * scan_msg.angle_increment)
            angle_deg = math.degrees(angle_rad)
            if deg_min <= angle_deg <= deg_max:
                result = min(result, self._valid_range(raw_value, max_range, range_min))

        return result

    def _distance_bucket(self, distance):
        if distance < self.blocked_distance:
            return "blocked"
        if distance < self.near_distance:
            return "near"
        return "clear"

    def _goal_direction_bucket(self, robot_x, robot_y, robot_yaw, goal_x, goal_y):
        desired_yaw = math.atan2(goal_y - robot_y, goal_x - robot_x)
        error = self.normalise_angle(desired_yaw - robot_yaw)

        if abs(error) <= math.radians(25):
            return "goal_front", error
        if math.radians(25) < error <= math.radians(100):
            return "goal_left", error
        if math.radians(-100) <= error < math.radians(-25):
            return "goal_right", error
        return "goal_behind", error

    def _goal_distance_bucket(self, distance):
        if distance <= self.goal_close_distance:
            return "goal_close"
        if distance <= self.goal_medium_distance:
            return "goal_medium"
        if distance <= self.goal_far_distance:
            return "goal_mid_far"
        return "goal_far"

    def encode(self, scan_msg, robot_x, robot_y, robot_yaw, goal_x, goal_y):
        """
        Return:
            state_key: string suitable for a Q-table key
            state_id: stable integer for logs/custom ROS message
            info: useful numeric details for reward and debugging
        """
        sector_distances = {}
        sector_buckets = {}

        for name, limits in self.sectors.items():
            sector_min = self._sector_min(scan_msg, limits[0], limits[1])
            sector_distances[name] = sector_min
            sector_buckets[name] = self._distance_bucket(sector_min)

        distance_to_goal = math.sqrt((goal_x - robot_x) ** 2 + (goal_y - robot_y) ** 2)
        goal_direction, goal_angle_error = self._goal_direction_bucket(
            robot_x, robot_y, robot_yaw, goal_x, goal_y
        )
        goal_distance = self._goal_distance_bucket(distance_to_goal)

        ordered_parts = [
            "F:" + sector_buckets["front"],
            "FL:" + sector_buckets["front_left"],
            "FR:" + sector_buckets["front_right"],
            "L:" + sector_buckets["left"],
            "R:" + sector_buckets["right"],
            goal_direction,
            goal_distance,
        ]
        state_key = "|".join(ordered_parts)

        info = {
            "sector_distances": sector_distances,
            "sector_buckets": sector_buckets,
            "front_distance": sector_distances["front"],
            "min_distance": min(sector_distances.values()),
            "distance_to_goal": distance_to_goal,
            "goal_angle_error": goal_angle_error,
            "goal_direction": goal_direction,
            "goal_distance": goal_distance,
        }

        return state_key, self.stable_state_id(state_key), info