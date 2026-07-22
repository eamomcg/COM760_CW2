import sys
import pandas as pd
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_results.py <episode_log_csv>")
        return

    csv_file = sys.argv[1]
    df = pd.read_csv(csv_file)

    # Convert columns explicitly to numpy arrays to avoid pandas/matplotlib version bugs
    episodes = df["episode"].to_numpy()
    rewards = df["total_reward"].to_numpy()
    
    # Calculate rolling success rate safely
    success = df["goal_reached"].to_numpy()
    success_series = pd.Series(success)
    success_rate = success_series.rolling(window=20, min_periods=1).mean().to_numpy()

    # Plot 1: Reward Curve
    plt.figure(figsize=(10, 5))
    plt.plot(episodes, rewards, color='blue', alpha=0.6)
    plt.title("Reward per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.grid(True)
    plt.savefig("reward_curve.png")
    plt.close()

    # Plot 2: Success Rate Curve
    plt.figure(figsize=(10, 5))
    plt.plot(episodes, success_rate * 100, color='green')
    plt.title("Success Rate (20-Episode Moving Average)")
    plt.xlabel("Episode")
    plt.ylabel("Success Rate (%)")
    plt.grid(True)
    plt.savefig("success_rate.png")
    plt.close()

    print("Successfully generated reward_curve.png and success_rate.png!")

if __name__ == "__main__":
    main()
