"""First learning checkpoint: inspect Rosa's simulator."""

import numpy as np
from starter import ZONES, TIME_BLOCKS, COSTS, PROMISE, delivery_times

print("Zones:", ZONES)
print("Time blocks:", TIME_BLOCKS)
print("Costs:", COSTS)

# Each array entry is one order's delivery time, measured in minutes.
times = delivery_times("Far West", "Fri/Sat eve", PROMISE, seed=1)
print(len(times), "orders; average delivery time", round(times.mean(), 1), "minutes")
print("First five delivery times:", times[:5])
