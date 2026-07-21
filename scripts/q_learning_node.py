#!/usr/bin/env python3
"""
Workstream A: Q-learning controller for the city delivery robot.

This node:
- subscribes to LaserScan and Odometry
- encodes the current state
- selects an action using epsilon-greedy Q-learning
- publishes Twist commands to /group34Bot/cmd_vel
- publishes a custom QLearningStatus message
- exposes a custom SetDeliveryGoal service
- calls /group34Bot/reset_episode between training episodes
"""

import json
import math
import os
import random
import sys
import time

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_srvs.srv import Empty
from tf.transformations import euler_from_quaternion

# Force Python to prioritize the local script directory for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import local helper classes.
from action_executor import ActionExecutor
from reward_manager import RewardManager
from state_encoder import StateEncoder
from training_logger import TrainingLogger

from com760cw2_group34.msg import QLearningStatus
from com760cw2_group34.srv import SetDeliveryGoal, SetDeliveryGoalResponse

class QLearningNode:
    def __init__(self):
        rospy.init_node("q_learning_delivery_node")

        self.package_name = rospy.get_param("~package_name", "com760cw2_group34")

        self.cmd_vel_topic = self.param("cmd_vel_topic", "/group34Bot/cmd_vel")
        self.scan_topic = self.param("scan_topic", "/group34Bot/laser/scan")
        self.odom_topic = self.param("odom_topic", "/odom")
        self.status_topic = self.param("status_topic", "/group34Bot/q_learning_status")
        self.reset_service_name = self.param("reset_service", "/group34Bot/reset_episode")

        self.mode = self.param("mode", "train")  # train or demo

        self.goal_x = float(self.param("goal_x", 6.0))
        self.goal_y = float(self.param("goal_y", 4.0))
        self.goal_tolerance = float(self.param("goal_tolerance", 0.45))

        self.max_episodes = int(self.param("max_episodes", 300))
        self.max_steps_per_episode = int(self.param("max_steps_per_episode", 400))
        self.control_rate_hz = float(self.param("control_rate_hz", 5.0))

        self.alpha = float(self.param("alpha", 0.30))
        self.gamma = float(self.param("gamma", 0.90))
        self.epsilon = float(self.param("epsilon", 1.00))
        self.epsilon_min = float(self.param("epsilon_min", 0.05))
        self.epsilon_decay = float(self.param("epsilon_decay", 0.995))

        # In demo mode we want the best known action, not random exploration.
        if self.mode == "demo":
            self.epsilon = 0.0

        self.results_dir = os.path.expanduser(self.param("results_dir", "~/catkin_ws/src/com760cw2_group34/results"))
        self.q_table_path = os.path.expanduser(self.param("q_table_path", os.path.join(self.results_dir, "q_table.json")))
        os.makedirs(self.results_dir, exist_ok=True)

        self.scan_msg = None
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.odom_ready = False

        self.encoder = StateEncoder(
            blocked_distance=float(self.param("blocked_distance", 0.45)),
            near_distance=float(self.param("near_distance", 1.00)),
            goal_close_distance=float(self.param("goal_close_distance", 0.60)),
            goal_medium_distance=float(self.param("goal_medium_distance", 2.50)),
        )
        self.action_executor = ActionExecutor(
            linear_speed=float(self.param("linear_speed", 0.20)),
            angular_speed=float(self.param("angular_speed", 0.65)),
        )
        self.reward_manager = RewardManager(
            goal_tolerance=self.goal_tolerance,
            collision_distance=float(self.param("collision_distance", 0.24)),
            near_obstacle_distance=float(self.param("near_obstacle_distance", 0.45)),
            goal_reward=float(self.param("goal_reward", 100.0)),
            collision_penalty=float(self.param("collision_penalty", -100.0)),
            step_penalty=float(self.param("step_penalty", -1.0)),
            progress_reward_scale=float(self.param("progress_reward_scale", 10.0)),
            moved_away_penalty=float(self.param("moved_away_penalty", -4.0)),
            near_obstacle_penalty=float(self.param("near_obstacle_penalty", -8.0)),
            turn_penalty=float(self.param("turn_penalty", -0.25)),
        )
        self.logger = TrainingLogger(self.results_dir)

        self.q_table = {}
        self.load_q_table()

        self.pub_cmd = rospy.Publisher(self.cmd_vel_topic, Twist, queue_size=1)
        self.pub_status = rospy.Publisher(self.status_topic, QLearningStatus, queue_size=10)

        self.sub_scan = rospy.Subscriber(self.scan_topic, LaserScan, self.scan_callback)
        self.sub_odom = rospy.Subscriber(self.odom_topic, Odometry, self.odom_callback)

        self.goal_service = rospy.Service("/group34Bot/set_delivery_goal", SetDeliveryGoal, self.handle_set_delivery_goal)

        rospy.loginfo("Q-learning node ready. mode=%s goal=(%.2f, %.2f)", self.mode, self.goal_x, self.goal_y)

    def param(self, name, default):
        """Read private parameter first, then global parameter, then default."""
        return rospy.get_param("~" + name, rospy.get_param(name, default))

    def scan_callback(self, msg):
        self.scan_msg = msg

    def odom_callback(self, msg):
        pose = msg.pose.pose
        self.robot_x = pose.position.x
        self.robot_y = pose.position.y
        quat = [
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z,
            pose.orientation.w,
        ]
        _, _, self.robot_yaw = euler_from_quaternion(quat)
        self.odom_ready = True

    def handle_set_delivery_goal(self, request):
        if request.tolerance <= 0.0:
            return SetDeliveryGoalResponse(False, "Tolerance must be greater than zero.")
        self.goal_x = request.goal_x
        self.goal_y = request.goal_y
        self.goal_tolerance = request.tolerance
        self.reward_manager.goal_tolerance = request.tolerance
        msg = "Delivery goal set to x=%.2f, y=%.2f, tolerance=%.2f" % (
            self.goal_x, self.goal_y, self.goal_tolerance
        )
        rospy.loginfo(msg)
        return SetDeliveryGoalResponse(True, msg)

    def wait_for_inputs(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown() and (self.scan_msg is None or not self.odom_ready):
            rospy.loginfo_throttle(2.0, "Waiting for scan and odometry: scan=%s odom=%s", self.scan_msg is not None, self.odom_ready)
            rate.sleep()

    def ensure_state(self, state_key):
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0 for _ in range(self.action_executor.action_count)]

    def select_action(self, state_key):
        self.ensure_state(state_key)
        if random.random() < self.epsilon:
            return random.randint(0, self.action_executor.action_count - 1)

        values = self.q_table[state_key]
        best_value = max(values)
        best_actions = [i for i, value in enumerate(values) if value == best_value]
        return random.choice(best_actions)

    def update_q_value(self, state_key, action_id, reward, next_state_key):
        self.ensure_state(state_key)
        self.ensure_state(next_state_key)

        old_q = self.q_table[state_key][action_id]
        next_best_q = max(self.q_table[next_state_key])
        new_q = old_q + self.alpha * (reward + self.gamma * next_best_q - old_q)
        self.q_table[state_key][action_id] = new_q

    def get_state(self):
        return self.encoder.encode(
            self.scan_msg,
            self.robot_x,
            self.robot_y,
            self.robot_yaw,
            self.goal_x,
            self.goal_y,
        )

    def publish_status(self, episode, step, state_id, action_id, reward, total_reward, collision, goal_reached):
        msg = QLearningStatus()
        msg.episode = int(episode)
        msg.step = int(step)
        msg.state_id = int(state_id)
        msg.action_id = int(action_id)
        msg.reward = float(reward)
        msg.total_reward = float(total_reward)
        msg.collision = bool(collision)
        msg.goal_reached = bool(goal_reached)
        self.pub_status.publish(msg)

    def reset_episode(self):
        self.pub_cmd.publish(self.action_executor.stop_twist())
        try:
            rospy.wait_for_service(self.reset_service_name, timeout=5.0)
            reset_proxy = rospy.ServiceProxy(self.reset_service_name, Empty)
            reset_proxy()
            rospy.sleep(0.8)
            return True
        except Exception as exc:
            rospy.logwarn("Could not call reset service %s: %s", self.reset_service_name, exc)
            return False

    def save_q_table(self):
        os.makedirs(os.path.dirname(self.q_table_path), exist_ok=True)
        with open(self.q_table_path, "w") as f:
            json.dump(self.q_table, f, indent=2, sort_keys=True)
        rospy.loginfo("Saved Q-table with %d states to %s", len(self.q_table), self.q_table_path)

    def load_q_table(self):
        if not os.path.exists(self.q_table_path):
            rospy.logwarn("No existing Q-table found at %s. Starting fresh.", self.q_table_path)
            self.q_table = {}
            return
        try:
            with open(self.q_table_path, "r") as f:
                self.q_table = json.load(f)
            rospy.loginfo("Loaded Q-table with %d states from %s", len(self.q_table), self.q_table_path)
        except Exception as exc:
            rospy.logwarn("Could not load Q-table: %s. Starting fresh.", exc)
            self.q_table = {}

    def run_episode(self, episode):
        self.reset_episode()
        # Wait a moment for the physics engine to stabilize after reset
        rospy.sleep(0.5)
        
        state_key, state_id, state_info = self.get_state()
        previous_distance = state_info["distance_to_goal"]
        total_reward = 0.0
        rate = rospy.Rate(self.control_rate_hz)

        goal_reached = False
        collision = False
        
        # Grace period: ignore collisions for the first few control loops
        grace_steps = 5

        for step in range(1, self.max_steps_per_episode + 1):
            if rospy.is_shutdown():
                break

            state_key, state_id, state_info = self.get_state()
            action_id = self.select_action(state_key)
            action_name = self.action_executor.get_action_name(action_id)
            self.pub_cmd.publish(self.action_executor.get_twist(action_id))
            rate.sleep()

            next_state_key, next_state_id, next_state_info = self.get_state()
            reward, done, goal_reached, collision = self.reward_manager.compute(
                previous_distance, next_state_info, action_id
            )

            # --- GRACE PERIOD OVERRIDE ---
            if step <= grace_steps:
                collision = False
                done = False
            # -----------------------------

            total_reward += reward

            if self.mode == "train":
                self.update_q_value(state_key, action_id, reward, next_state_key)

            self.publish_status(
                episode, step, state_id, action_id, reward, total_reward, collision, goal_reached
            )
            self.logger.log_step(
                episode, step, state_id, action_id, action_name, reward, total_reward,
                next_state_info["distance_to_goal"], next_state_info["min_distance"],
                self.epsilon, goal_reached, collision
            )

            previous_distance = next_state_info["distance_to_goal"]

            if done:
                self.pub_cmd.publish(self.action_executor.stop_twist())
                self.logger.log_episode(episode, step, total_reward, self.epsilon, goal_reached, collision)
                return step, total_reward, goal_reached, collision

        self.pub_cmd.publish(self.action_executor.stop_twist())
        self.logger.log_episode(episode, self.max_steps_per_episode, total_reward, self.epsilon, goal_reached, collision)
        return self.max_steps_per_episode, total_reward, goal_reached, collision

    def run(self):
        self.wait_for_inputs()

        if self.mode == "demo":
            rospy.loginfo("Running demo mode using trained Q-table.")
            self.max_episodes = 1
        else:
            rospy.loginfo("Running training mode for %d episodes.", self.max_episodes)

        for episode in range(1, self.max_episodes + 1):
            if rospy.is_shutdown():
                break

            steps, total_reward, goal_reached, collision = self.run_episode(episode)
            rospy.loginfo(
                "Episode %d finished: steps=%d total_reward=%.2f goal=%s collision=%s epsilon=%.3f",
                episode, steps, total_reward, goal_reached, collision, self.epsilon
            )

            if self.mode == "train":
                self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
                if episode % 10 == 0:
                    self.save_q_table()

        if self.mode == "train":
            self.save_q_table()
        self.pub_cmd.publish(self.action_executor.stop_twist())


if __name__ == "__main__":
    try:
        QLearningNode().run()
    except rospy.ROSInterruptException:
        pass
