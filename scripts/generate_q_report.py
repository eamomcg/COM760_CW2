#!/usr/bin/env python3
"""
Generates an objective Action Advantage plot from the Q-table.
Calculates: Q(forward) - Max(Q(turn)) per state.
Configured for headless execution (Agg backend) and proper LaTeX rendering.
"""

import json
import os
import matplotlib
# Force the 'Agg' backend to prevent GDK/Display errors in headless environments.
# This MUST be called before importing pyplot.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_advantage_report():
    q_table_path = "/home/b00992264/com760_ws/src/com760cw2_group34/results/large_city/q_table_large_city.json"
    
    if not os.path.exists(q_table_path):
        print(f"Error: Q-table not found at {q_table_path}")
        return

    with open(q_table_path, "r") as f:
        q_table = json.load(f)

    forward_advantages = []
    turn_preferred_states = 0
    total_valid_states = 0
    
    forward_action_idx = 0
    turn_action_indices = [1, 2]

    for state, actions in q_table.items():
        q_values = []
        if isinstance(actions, dict):
            q_values = [float(actions.get(str(i), 0.0)) for i in range(len(actions))]
        elif isinstance(actions, list):
            q_values = [float(v) for v in actions]

        if len(q_values) >= 3:
            q_forward = q_values[forward_action_idx]
            q_turn = max([q_values[i] for i in turn_action_indices if i < len(q_values)])
            
            if q_forward == 0.0 and q_turn == 0.0:
                continue
                
            advantage = q_forward - q_turn
            forward_advantages.append(advantage)
            total_valid_states += 1
            
            if advantage < 0:
                turn_preferred_states += 1

    if not forward_advantages:
        print("No valid visited states found to compare.")
        return

    plt.figure(figsize=(10, 6))
    
    n, bins, patches = plt.hist(forward_advantages, bins=50, edgecolor='black', alpha=0.8)
    
    for i in range(len(patches)):
        if bins[i] < 0:
            patches[i].set_facecolor('indianred')
        else:
            patches[i].set_facecolor('steelblue')

    plt.title("Distribution of Forward Action Advantage Across Visited States", fontsize=14)
    # Use raw string (r) and double braces ({{}}) for correct LaTeX rendering inside f-strings
    plt.xlabel(r"Advantage Score: $Q_{forward} - \max(Q_{turn})$", fontsize=12)
    plt.ylabel("Frequency (States)", fontsize=12)
    plt.axvline(x=0, color='black', linestyle='--', linewidth=1.5, label=r'Equilibrium ($Q_{forward} = \max(Q_{turn})$)')
    
    turn_pct = (turn_preferred_states / total_valid_states) * 100
    
    # Double curly braces prevent Python from treating LaTeX subscripts as variables
    annotation_text = rf'{turn_pct:.1f}% of states exhibit' + '\n' + r'$\max(Q_{turn}) > Q_{forward}$'
    
    plt.annotate(annotation_text, 
                 xy=(-5, max(n)*0.8), xytext=(-50, max(n)*0.9),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                 fontsize=11, backgroundcolor='white')

    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right')
    
    output_path = "/home/b00992264/com760_ws/src/com760cw2_group34/results/action_advantage_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph generated: {output_path}")

if __name__ == "__main__":
    generate_advantage_report()