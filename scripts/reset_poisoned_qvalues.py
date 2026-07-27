#!/usr/bin/env python3
"""
Targeted reset of Q-values that were poisoned by forward motion getting
blamed for later collisions, in states where the obstacle is only 'near'
(not 'blocked'). This lets those specific (state, action) pairs get
re-evaluated fresh under the rebalanced reward weights, without discarding
everything else the table has already learned (turning behavior, sector
recognition, genuinely-blocked-state caution, goal-direction logic, etc).

Actions: 0=forward, 1=turn_left, 2=turn_right, 3=forward_left, 4=forward_right, 5=stop
Only forward-moving actions (0, 3, 4) are touched, and only when the sector
relevant to that action reads 'near' (not 'blocked' -- blocked-state caution
is legitimate and left untouched).
"""

import json
import sys

INPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "q_table.json"
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "q_table.json"

with open(INPUT_PATH) as f:
    q_table = json.load(f)

reset_count = 0
touched_states = 0

for state_key, values in q_table.items():
    parts = state_key.split("|")
    # parts[0]="F:xxx", parts[1]="FL:xxx", parts[2]="FR:xxx"
    sector = {}
    for p in parts[:5]:
        name, bucket = p.split(":")
        sector[name] = bucket

    changed_this_state = False

    # forward (action 0): reset if the front sector is 'near'
    if sector.get("F") == "near" and values[0] != 0.0:
        values[0] = 0.0
        reset_count += 1
        changed_this_state = True

    # forward_left (action 3): reset if front or front-left is 'near'
    if (sector.get("F") == "near" or sector.get("FL") == "near") and values[3] != 0.0:
        values[3] = 0.0
        reset_count += 1
        changed_this_state = True

    # forward_right (action 4): reset if front or front-right is 'near'
    if (sector.get("F") == "near" or sector.get("FR") == "near") and values[4] != 0.0:
        values[4] = 0.0
        reset_count += 1
        changed_this_state = True

    if changed_this_state:
        touched_states += 1

with open(OUTPUT_PATH, "w") as f:
    json.dump(q_table, f, indent=2, sort_keys=True)

print(f"Total states in table: {len(q_table)}")
print(f"States touched: {touched_states}")
print(f"Individual Q-values reset to 0.0: {reset_count}")
print(f"Written to: {OUTPUT_PATH}")