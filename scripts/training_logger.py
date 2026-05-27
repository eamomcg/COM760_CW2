#!/usr/bin/env python3
"""
Workstream A: CSV logging for report evidence.
"""

import csv
import os
import time


class TrainingLogger:
    def __init__(self, results_dir):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.step_log_path = os.path.join(results_dir, "step_log_%s.csv" % timestamp)
        self.episode_log_path = os.path.join(results_dir, "episode_log_%s.csv" % timestamp)

        self._create_file(self.step_log_path, [
            "episode", "step", "state_id", "action_id", "action_name",
            "reward", "total_reward", "distance_to_goal", "min_distance",
            "epsilon", "goal_reached", "collision"
        ])
        self._create_file(self.episode_log_path, [
            "episode", "steps", "total_reward", "epsilon", "goal_reached", "collision"
        ])

    @staticmethod
    def _create_file(path, header):
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

    def log_step(self, episode, step, state_id, action_id, action_name,
                 reward, total_reward, distance_to_goal, min_distance,
                 epsilon, goal_reached, collision):
        with open(self.step_log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                episode, step, state_id, action_id, action_name,
                round(reward, 4), round(total_reward, 4),
                round(distance_to_goal, 4), round(min_distance, 4),
                round(epsilon, 5), goal_reached, collision
            ])

    def log_episode(self, episode, steps, total_reward, epsilon, goal_reached, collision):
        with open(self.episode_log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                episode, steps, round(total_reward, 4), round(epsilon, 5),
                goal_reached, collision
            ])
