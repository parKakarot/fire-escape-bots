# sim.py - the fire, the path finding, the 4 bots, and the game itself

import random
import heapq

from ship import neighbors, open_cells, render


# picks 3 different random open cells for the bot, the button and the fire
def place_things(grid, rng = random):
    cells = open_cells(grid)

    # remove each picked cell so two things can't land on the same cell
    bot = rng.choice(cells)
    cells.remove(bot)

    button = rng.choice(cells)
    cells.remove(button)

    fire = rng.choice(cells)

    return bot, button, fire


# the fire spreads by one time step
# fire is the set of cells that are burning right now
def advance_fire(grid, fire, q, rng = random):
    D = len(grid)
    new_fire = set()

    for r in range(D):
        for c in range(D):
            # walls can't burn, and cells already on fire stay on fire
            if not grid[r][c]:
                continue

            if (r, c) in fire:
                continue

            # k = how many neighbors are on fire
            k = 0
            for cell in neighbors(D, r, c):
                if cell in fire:
                    k += 1

            # each burning neighbor spreads to this cell with chance q.
            # (1 - q) ** k = the chance that NONE of them spread, so 1 minus that = at least one did
            if k > 0:
                chance = 1 - (1 - q) ** k
                if rng.random() < chance:
                    new_fire.add((r, c))

    # add the new fire AFTER checking every cell so the fire can't spread twice in one step
    for cell in new_fire:
        fire.add(cell)


# BFS: finds the shortest path from start to goal
# blocked = cells the path can't use (like the fire)
def shortest_path(grid, start, goal, blocked):
    if start in blocked:
        return None
    if goal in blocked:
        return None

    D = len(grid)
    queue = [start]
    # came_from remembers which cell we came from to reach each cell.
    # it also works as the "visited" set: if a cell is in came_from we already found it
    came_from = {}
    came_from[start] = None

    while len(queue) > 0:
        # pop from the front (first in, first out), so closer cells get explored first
        current = queue.pop(0)

        if current == goal:
            # walk back from the goal to the start to get the path
            path = []
            step = goal
            while step != None:
                path.append(step)
                step = came_from[step]
            path.reverse()
            return path

        r = current[0]
        c = current[1]
        for cell in neighbors(D, r, c):
            if not grid[cell[0]][cell[1]]:
                continue
            if cell in blocked:
                continue
            if cell in came_from:
                continue
            came_from[cell] = current
            queue.append(cell)

    return None


#  BOTS 
# every bot gets the same inputs and gives back the cell it wants to move to



# bot 1: plans once at the start and never re-plans
def bot1(grid, bot, button, fire, state):
    # first turn: make the plan and save it in state so we remember it on the next turns
    if "plan" not in state:
        state["plan"] = shortest_path(grid, bot, button, fire)
        state["step"] = 0

    plan = state["plan"]
    # no path at the start, so just stay put
    if plan == None:
        return bot
    # already at the end of the plan
    if state["step"] + 1 >= len(plan):
        return bot

    # follow the plan blindly, even if the fire is in the way now
    state["step"] = state["step"] + 1
    return plan[state["step"]]


# bot 2: re-plans every turn and avoids the cells on fire right now
def bot2(grid, bot, button, fire, state):
    path = shortest_path(grid, bot, button, fire)

    if path == None:
        return bot
    if len(path) < 2:
        return bot

    # path[0] is where the bot is now, so path[1] is the next step
    return path[1]


# bot 3: re-plans every turn and avoids the fire AND the cells next to the fire 
def bot3(grid, bot, button, fire, state):
    D = len(grid)

    # the danger zone = the fire + every cell next to the fire
    danger = set()
    for fire_cell in fire:
        danger.add(fire_cell)
        for cell in neighbors(D, fire_cell[0], fire_cell[1]):
            danger.add(cell)

    # try the safe route first
    path = shortest_path(grid, bot, button, danger)

    # if not then just avoid the fire
    if path == None:
        path = shortest_path(grid, bot, button, fire)

    if path == None:
        return bot
    if len(path) < 2:
        return bot

    return path[1]


# bot 4: races the fire. uses two BFS maps and an A* search where risky steps cost more


# BFS from one or more starting cells, with no goal
# gives back a dictionary: cell -> how many steps it is from the closest starting cell
def bfs_distances(grid, sources):
    D = len(grid)
    dist = {}
    queue = []
    for cell in sources:
        dist[cell] = 0
        queue.append(cell)

    while len(queue) > 0:
        current = queue.pop(0)
        for cell in neighbors(D, current[0], current[1]):
            if not grid[cell[0]][cell[1]]:
                continue
            if cell in dist:
                continue
            dist[cell] = dist[current] + 1
            queue.append(cell)

    return dist


# how much it costs to step onto a cell
# fire_steps = how far the fire is from the cell, t = the turn the bot would get there
# the cost is 1 if the bot gets there way before the fire, and up to 11 if it's a close race
def step_cost(fire_steps, t, q):
    if fire_steps == None:
        return 1
    if q == 0:
        return 1

    # the fire moves about q cells per turn on average,
    # fire time (formula 1)
    fire_time = fire_steps / q
    # ratio near 0 = the bot is way ahead of the fire, ratio 1 or more = the fire probably wins
    # ratio (formula 2)
    ratio = t / fire_time

    # risk (formula 3)
    if ratio < 0.5:
        risk = 0
    elif ratio < 1:
        risk = (ratio - 0.5) / 0.5
    else:
        risk = 1

    # step cost (formula 4)
    return 1 + 10 * risk


# A* pathfinding notes:


# goal: find the CHEAPEST path from the bot to the button, not just the shortest one.
#      some steps cost more (the ones where the fire might get there before me), so a plain BFS
#       won't work, because BFS only counts steps and treats every step the same.

# what i NEED:
#  g for every cell = the cheapest cost i found so far to get there (best_cost)
# h for every cell = how far it is from the button (from the BFS from the button)
# f = g + h = my guess of the total cost if i go through that cell
# a priority queue so i can always grab the cell with the smallest f (heapq does this for me)
# came_from so i can walk back from the button to the start, same as in my BFS
# steps for every cell, because how much a step costs depends on WHEN i get there
# a done set so i don't explore the same cell twice


#  plan for the loop:
# 1. pop the cell with the smallest f, while the queue isn't empty
# 2. if i already explored it, skip it (it's an old copy that was more expensive)
# 3. if it's the button, walk back through came_from and return the path
# 4. otherwise look at each neighbor and skip walls, fire, and cells i already explored
# 5. figure out what turn i'd get to the neighbor (t) and how much that step costs (step_cost)
# 6. if that's cheaper than any way i found before, save it and push the neighbor with f = g + h
# 7. if the queue runs out, i never reached the button, so there's no path (return None)



def astar_path(grid, start, goal, fire, fire_dist, h, q):
    D = len(grid)
    if goal in fire:
        return None

    best_cost = {}
    steps = {}
    came_from = {}
    done = set()
    best_cost[start] = 0
    steps[start] = 0
    came_from[start] = None

    # the priority queue holds (f, g, cell). heappop always gives back the one with the smallest f
    queue = []
    heapq.heappush(queue, (h[start], 0, start))



    while len(queue) > 0:
        item = heapq.heappop(queue)
        g = item[1]
        current = item[2]

        if current in done:
            continue
        done.add(current)

        if current == goal:
            # walk back from the goal to the start to get the path
            path = [] 
            step = goal


            while step != None:
                path.append(step)
                step = came_from[step]
            path.reverse()
            return path

        for n in neighbors(D, current[0], current[1]):
            if not grid[n[0]][n[1]]:
                continue
            if n in fire:
                continue
            if n in done:
                continue 
            # not in h means the button can't be reached from n, so it's useless
            if n not in h:
                continue

            # t = the turn the bot would get to n.
            # the game ends as soon as the bot reaches the button (before the fire spreads that turn),
            # so the button gets one turn less of fire risk
            t = steps[current] + 1
            if n == goal:
                t = t - 1

            if n in fire_dist:
                fire_steps = fire_dist[n]
            else:
                fire_steps = None

            new_g = g + step_cost(fire_steps, t, q)

            # check whether this is the cheapest cost so far
            found_cheaper = False
            if n not in best_cost:
                found_cheaper = True
            elif new_g < best_cost[n]:
                found_cheaper = True

            if found_cheaper:
                best_cost[n] = new_g
                steps[n] = steps[current] + 1
                came_from[n] = current
                f = new_g + h[n]
                heapq.heappush(queue, (f, new_g, n))

    return None


def bot4(grid, bot, button, fire, state):
    q = state["q"]
    # fire_dist = how far each cell is from the fire (used to price risky steps)
    # h = how far each cell is from the button (the A* guess)
    # both get redone every turn because the fire keeps growing
    fire_dist = bfs_distances(grid, fire)
    h = bfs_distances(grid, [button])
    path = astar_path(grid, bot, button, fire, fire_dist, h, q)

    if path == None:
        return bot
    if len(path) < 2:
        return bot

    return path[1]


# THE GAME 
# plays one whole game. gives back True if the bot wins and False if it loses
def run_simulation(grid, q, bot_function, rng = random, show = False):
    places = place_things(grid, rng)
    bot = places[0]
    button = places[1]
    fire_start = places[2]

    fire = set()
    fire.add(fire_start)

    # state is a dictionary the bot can use to remember things between turns (bot 1 saves its plan here)
    state = {}
    state["q"] = q

    # safety limit so a game can't go on forever
    D = len(grid)
    max_turns = D * D * 4

    for t in range(1, max_turns + 1):
        bot = bot_function(grid, bot, button, fire, state)

        # check the fire FIRST: if the bot walks onto a cell that's burning (even the button), it loses
        #  if the bot and the fire are ever on the same cell, the task is failed)
        if bot in fire:
            return False

        if bot == button:
            return True

        advance_fire(grid, fire, q, rng)

        # the fire might have spread onto the bot
        if bot in fire:
            return False

        if show:
            labels = {}
            for cell in fire:
                labels[cell] = "F"
            labels[button] = "X"
            labels[bot] = "B"
            print("step", t)
            print(render(grid, labels))
            print()

    return False
