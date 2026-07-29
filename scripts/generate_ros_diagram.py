#!/usr/init/env python3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def main():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Color Palette & Styles
    c_gazebo = "#D6Eaf8"    # Soft Blue
    c_node = "#E8F8F5"      # Soft Teal/Mint
    c_support = "#FCF3CF"   # Soft Yellow
    
    box_gazebo = dict(boxstyle="round,pad=0.6", fc=c_gazebo, ec="#2980B9", lw=2)
    box_main = dict(boxstyle="round,pad=0.7", fc=c_node, ec="#16A085", lw=2)
    box_sup = dict(boxstyle="round,pad=0.6", fc=c_support, ec="#F39C12", lw=2)

    # 1. Draw Core System Nodes (Ovals/Rounded Rectangles)
    ax.text(2.2, 6.2, "Gazebo Simulation Engine\n(/gazebo)", ha="center", va="center", fontsize=10, fontweight="bold", bbox=box_gazebo)
    ax.text(6.0, 3.5, "Q-Learning Delivery Node\n(/q_learning_delivery_node)\n\n• StateEncoder (LiDAR & Odom)\n• RewardManager (Shaped Rewards)\n• ActionExecutor (Epsilon-Greedy)", ha="center", va="center", fontsize=9.5, fontweight="bold", bbox=box_main)
    ax.text(1.8, 1.8, "Episode Resetter\n(/episode_resetter)", ha="center", va="center", fontsize=9, fontweight="bold", bbox=box_sup)
    ax.text(9.8, 6.2, "Mobile Obstacle Controller\n(/mobile_obstacle_controller)", ha="center", va="center", fontsize=9, fontweight="bold", bbox=box_sup)

    # 2. Draw Directed Topic & Service Connections with Annotations
    arrow_props = dict(facecolor='#2C3E50', edgecolor='#2C3E50', arrowstyle='->', lw=1.5, shrinkA=8, shrinkB=8)

    # Sensor Streams (Gazebo -> Q-Node)
    ax.annotate("", xy=(4.3, 4.3), xytext=(2.8, 5.6), arrowprops=arrow_props)
    ax.text(3.1, 5.1, "/group34Bot/laser/scan\n/odom", fontsize=8.5, color="#C0392B", fontweight="bold", rotation=36)

    # Actuator Commands (Q-Node -> Gazebo)
    ax.annotate("", xy=(2.6, 5.6), xytext=(4.3, 4.0), arrowprops=arrow_props)
    ax.text(4.0, 4.5, "/group34Bot/cmd_vel", fontsize=8.5, color="#27AE60", fontweight="bold", rotation=-36)

    # Dynamic Obstacle Service (Obstacle Controller -> Gazebo)
    ax.annotate("", xy=(3.5, 6.5), xytext=(8.0, 6.5), arrowprops=arrow_props)
    ax.text(5.6, 6.7, "/gazebo/set_model_state (Service)", fontsize=8.5, color="#2980B9", fontweight="bold")

    # Episode Resetter Service (Q-Node -> Resetter)
    ax.annotate("", xy=(2.8, 2.2), xytext=(4.8, 2.8), arrowprops=arrow_props)
    ax.text(3.4, 2.3, "/group34Bot/reset_episode (Service)", fontsize=8.5, color="#8E44AD", fontweight="bold", rotation=18)

    # Title & Caption Layout
    plt.title("Fig. 1. Advanced ROS Node Computation Graph and Topic/Service Topology", fontsize=11.5, fontweight="bold", pad=15)

    output_path = "ros_node_architecture.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated high-grade architecture diagram at: {output_path}")

if __name__ == "__main__":
    main()