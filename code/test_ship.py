import random

from ship import generate_ship, is_dead_end, neighbors, open_cells, render

#test file to check that ship actually builds
D = 50
SEED = 2


# checks that every open cell can reach every other open cell
def is_connected(grid):
    cells = open_cells(grid)
    start = cells[0]
    seen = set()
    seen.add(start)
    stack = [start]
    while len(stack) > 0:
        r, c = stack.pop()
        for nr, nc in neighbors(len(grid), r, c):
            if grid[nr][nc] and (nr, nc) not in seen:
                seen.add((nr, nc))
                stack.append((nr, nc))
    # if we reached as many cells as there are open cells, everything is connected
    return len(seen) == len(cells)


grid = generate_ship(D, random.Random(SEED))
cells = open_cells(grid)

# count the dead ends
dead_end_count = 0
for r, c in cells:
    if is_dead_end(grid, r, c):
        dead_end_count += 1

print(render(grid))
print()
print("open cells:", len(cells), "/", D * D)
print("dead ends:", dead_end_count)
print("all open cells connected:", is_connected(grid))
