#!/usr/bin/env python3
"""
Optional shared script: creates simple plots from an episode CSV.
Run outside ROS, for example:
python3 scripts/plot_results.py results/episode_log_YYYYMMDD-HHMMSS.csv
"""

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_results.py <episode_log.csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    df = pd.read_csv(csv_path)
    out_dir = os.path.dirname(csv_path)

    plt.figure()
    plt.plot(df["episode"], df["total_reward"])
    plt.xlabel("Episode")
    plt.ylabel("Total reward")
    plt.title("Q-learning reward per episode")
    plt.grid(True)
    reward_path = os.path.join(out_dir, "reward_curve.png")
    plt.savefig(reward_path, bbox_inches="tight")

    plt.figure()
    success_rate = df["goal_reached"].rolling(window=20, min_periods=1).mean()
    plt.plot(df["episode"], success_rate)
    plt.xlabel("Episode")
    plt.ylabel("Success rate, rolling 20 episodes")
    plt.title("Q-learning success rate")
    plt.grid(True)
    success_path = os.path.join(out_dir, "success_rate.png")
    plt.savefig(success_path, bbox_inches="tight")

    print("Saved:")
    print(reward_path)
    print(success_path)


if __name__ == "__main__":
    main()
