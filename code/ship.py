# ship.py - makes the ship layout
# the ship is a D x D grid (a list of lists)

import random


# gives back the cells up, down, left and right of (r, c) that are inside the grid
def neighbors(D, r, c):
    result = []
    if r - 1 >= 0:
        result.append((r - 1, c))
    if r + 1 < D:
        result.append((r + 1, c))
    if c - 1 >= 0:
        result.append((r, c - 1))
    if c + 1 < D:
        result.append((r, c + 1))
    return result


# counts how many neighbors of (r, c) are open
def count_open_neighbors(grid, r, c):
    D = len(grid)
    count = 0
    for cell in neighbors(D, r, c):
        nr = cell[0]
        nc = cell[1]
        if grid[nr][nc]:
            count += 1
    return count


# a dead end is an open cell with exactly one open neighbor
def is_dead_end(grid, r, c):
    if not grid[r][c]:
        return False
    if count_open_neighbors(grid, r, c) == 1:
        return True
    return False


# gives back a list of every open cell
def open_cells(grid):
    D = len(grid)
    cells = []
    for r in range(D):
        for c in range(D):
            if grid[r][c]:
                cells.append((r, c))
    return cells


def generate_ship(D, rng=random):
    # start with every cell blocked
    grid = []
    for r in range(D):
        row = []
        for c in range(D):
            row.append(False)
        grid.append(row)

    # step 1: open a random cell that isn't on the edge
    r = rng.randrange(1, D - 1)
    c = rng.randrange(1, D - 1)
    grid[r][c] = True

    # step 2: keep opening a random blocked cell that has exactly one open neighbor
    # candidates = blocked cells that have exactly one open neighbor right now
    candidates = set()
    for cell in neighbors(D, r, c):
        candidates.add(cell)

    while len(candidates) > 0:
        # rng.choice needs a list, so copy the set into a list
        candidate_list = []
        for cell in candidates:
            candidate_list.append(cell)
        picked = rng.choice(candidate_list)
        r = picked[0]
        c = picked[1]

        grid[r][c] = True
        if (r, c) in candidates:
            candidates.remove((r, c))

        # opening this cell only changes its neighbors, so only check those
        for cell in neighbors(D, r, c):
            nr = cell[0]
            nc = cell[1]
            if not grid[nr][nc]:
                if count_open_neighbors(grid, nr, nc) == 1:
                    candidates.add((nr, nc))
                else:
                    if (nr, nc) in candidates:
                        candidates.remove((nr, nc))

    # step 3: find all the dead ends
    dead_ends = set()
    for cell in open_cells(grid):
        if is_dead_end(grid, cell[0], cell[1]):
            dead_ends.add(cell)

    target = len(dead_ends) // 2

    # open a random closed neighbor of a random dead end, until half the dead ends are gone
    while len(dead_ends) > target:
        dead_end_list = []
        for cell in dead_ends:
            dead_end_list.append(cell)
        picked = rng.choice(dead_end_list)
        r = picked[0]
        c = picked[1]

        # the blocked neighbors of this dead end
        closed_neighbors = []
        for cell in neighbors(D, r, c):
            if not grid[cell[0]][cell[1]]:
                closed_neighbors.append(cell)

        picked = rng.choice(closed_neighbors)
        nr = picked[0]
        nc = picked[1]
        grid[nr][nc] = True

        # only the cell we just opened and its neighbors can stop or start being dead ends
        to_check = []
        to_check.append((nr, nc))
        for cell in neighbors(D, nr, nc):
            to_check.append(cell)

        for cell in to_check:
            if is_dead_end(grid, cell[0], cell[1]):
                dead_ends.add(cell)
            else:
                if cell in dead_ends:
                    dead_ends.remove(cell)

    return grid


# draws the ship as text: '.' is open and '#' is blocked
# labels is a dictionary like {(3, 4): "B"} that draws a letter on a cell
def render(grid, labels=None):
    if labels == None:
        labels = {}

    D = len(grid)
    text = ""
    for r in range(D):
        row_text = ""
        for c in range(D):
            if (r, c) in labels:
                row_text = row_text + labels[(r, c)]
            elif grid[r][c]:
                row_text = row_text + "."
            else:
                row_text = row_text + "#"
        text = text + row_text
        if r < D - 1:
            text = text + "\n"
    return text
