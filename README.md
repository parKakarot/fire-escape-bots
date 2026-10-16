# Fire Escape Bots

A bot has to reach a button on a spaceship that is on fire. The fire spreads at random, and the bot loses if it ever ends up on a burning cell. This project builds the ship, simulates the fire, and compares four bot strategies over thousands of games.

Written for Project 1 of CS 440 (Intro to AI). The full analysis is in [`Proj1 Write Up.pdf`](Proj1%20Write%20Up.pdf).

## How it works

**The ship** ([`code/ship.py`](code/ship.py)) is a D×D grid. It starts fully blocked. The generator opens one random interior cell, then keeps opening blocked cells that have exactly one open neighbor, which grows a maze of corridors. At the end it opens extra cells next to about half of the dead ends, so the ship has some loops.

**The fire** ([`code/sim.py`](code/sim.py)) starts on one random open cell. Each turn, an open cell with `k` burning neighbors catches fire with probability `1 - (1 - q)^k`. The parameter `q` (between 0 and 1) sets how fast the fire spreads.

**Each turn:** the bot moves one cell. If it lands on fire it loses, and if it lands on the button it wins. Then the fire spreads, and if it spreads onto the bot, the bot loses.

## The bots

| Bot | Strategy |
|-----|----------|
| Bot 1 | Finds the shortest path once, at the start, and follows it without re-planning. |
| Bot 2 | Re-plans the shortest path every turn and avoids cells that are currently burning. |
| Bot 3 | Re-plans every turn and avoids burning cells and the cells next to them, if it can. |
| Bot 4 | Races the fire. It uses BFS to find how far the fire is from each cell, then runs A* where a step costs more the closer the race with the fire is (from 1 up to 11). |

## Results

Each bot played the same 300 games (60 ships of size 40×40, 5 games per ship) at each value of `q`. All bots got the same random seed for a given game, so they faced the same layout and the same fire.

Success rate at selected values of `q`:

| q    | Bot 1 | Bot 2 | Bot 3 | Bot 4 |
|------|-------|-------|-------|-------|
| 0.05 | 0.973 | 1.000 | 1.000 | 1.000 |
| 0.10 | 0.940 | 0.977 | 0.977 | 0.980 |
| 0.20 | 0.890 | 0.923 | 0.937 | 0.937 |
| 0.30 | 0.860 | 0.880 | 0.880 | 0.907 |
| 0.40 | 0.823 | 0.847 | 0.843 | 0.860 |
| 0.50 | 0.740 | 0.753 | 0.760 | 0.770 |
| 1.00 | 0.500 | 0.500 | 0.500 | 0.493 |

Bot 1 does worst at almost every value of `q` because it never re-plans. Bot 4 matches or beats the others across most of the range and gains the most around `q` = 0.3. At very high `q` the fire spreads so fast that strategy hardly matters.

The full tables are in [`code/results.csv`](code/results.csv) and [`code/results_two.csv`](code/results_two.csv) (a finer sweep from 0.04 to 0.5). The graphs are in [`Graphs.pdf`](Graphs.pdf).

## Running it

You need Python 3. Only the standard library is used.

```bash
cd code
python test_ship.py        # builds a 50x50 ship, prints it, and checks that it is connected
python experiment.py       # experiment 1, writes results.csv
python experiment_two.py   # experiment 2, writes results_two.csv
```

To watch a single game step by step:

```python
import random
from ship import generate_ship
from sim import run_simulation, bot4

grid = generate_ship(20, random.Random(0))
run_simulation(grid, 0.3, bot4, random.Random(0), show=True)
```

In the printout, `#` is a wall, `.` is open, `B` is the bot, `X` is the button, and `F` is fire.

## Files

```
code/
  ship.py            ship generation and rendering
  sim.py             fire spread, pathfinding, the four bots, and the game loop
  test_ship.py       checks that ship generation works
  experiment.py      experiment 1 (q from 0.01 to 1.0)
  experiment_two.py  experiment 2 (finer q from 0.04 to 0.5)
  results.csv        output of experiment 1
  results_two.csv    output of experiment 2
Graphs.pdf / .xls    plots of the results
Proj1 Write Up.pdf   the report
```
