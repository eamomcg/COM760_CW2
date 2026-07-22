#!/usr/bin/env python3
"""
Workstream A: reward shaping for Q-learning navigation.

The reward function should be simple enough to explain in the report:
- strongly reward reaching the delivery goal
- strongly punish collisions or unsafe closeness
- mildly reward progress toward the goal
- mildly punish wasted steps/spinning

FIX: previously this code re-filtered min_distance/front_distance with
"<= 0.08 -> 999.0 (clear)". state_encoder.py already sanitizes raw scan
values properly (NaN/Inf -> clear, saturated-at-floor -> near/contact), so
re-applying a second, cruder filter here was silently converting genuine
collisions into "nothing detected" and removing the collision_penalty signal
entirely. That filter has been removed; only NaN/Inf are treated as "no
reading" here now, as a defensive fallback.
"""

import math


class RewardManager:
    def __init__(self,
                 goal_tolerance=0.45,
                 collision_distance=0.24,
                 near_obstacle_distance=0.45,
                 goal_reward=100.0,
                 collision_penalty=-100.0,
                 step_penalty=-1.0,
                 progress_reward_scale=10.0,
                 moved_away_penalty=-4.0,
                 near_obstacle_penalty=-8.0,
                 turn_penalty=-0.25):
        self.goal_tolerance = goal_tolerance
        self.collision_distance = collision_distance
        self.near_obstacle_distance = near_obstacle_distance
        self.goal_reward = goal_reward
        self.collision_penalty = collision_penalty
        self.step_penalty = step_penalty
        self.progress_reward_scale = progress_reward_scale
        self.moved_away_penalty = moved_away_penalty
        self.near_obstacle_penalty = near_obstacle_penalty
        self.turn_penalty = turn_penalty

    def compute(self, previous_distance_to_goal, current_info, action_id):
        current_distance = current_info["distance_to_goal"]
        min_distance = current_info["min_distance"]
        front_distance = current_info["front_distance"]

        # Only guard against genuinely invalid values here. Do NOT treat
        # small distances as invalid -- state_encoder.py already turned
        # "sensor saturated at its floor" into range_min, which is a real,
        # meaningful near-collision reading and must reach the collision
        # check below.
        if min_distance is None or math.isnan(min_distance) or math.isinf(min_distance):
            min_distance = 999.0
        if front_distance is None or math.isnan(front_distance) or math.isinf(front_distance):
            front_distance = 999.0

        goal_reached = current_distance <= self.goal_tolerance
        collision = min_distance <= self.collision_distance

        if goal_reached:
            return self.goal_reward, True, True, False

        if collision:
            return self.collision_penalty, True, False, True

        reward = self.step_penalty

        progress = previous_distance_to_goal - current_distance
        if progress > 0.0:
            reward += progress * self.progress_reward_scale
        else:
            reward += self.moved_away_penalty

        if front_distance < self.near_obstacle_distance:
            reward += self.near_obstacle_penalty

        if action_id in [1, 2]:
            reward += self.turn_penalty

        return reward, False, False, False