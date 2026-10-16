# experiment 1: play lots of games for every bot at a bunch of q values
# saves the success rates to results.csv 

import random

from ship import generate_ship
from sim import run_simulation, bot1, bot2, bot3, bot4

# settings
ship_size = 40
num_ships = 60
games_for_ship = 5
Q_VALUES = [0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]

total_games = num_ships * games_for_ship

# make the ships first. ship i uses seed i, so the ships are the same every run
ships = []
for i in range(num_ships):
    ship = generate_ship(ship_size, random.Random(i))
    ships.append(ship)

# success rate of each bot at each q
bot1_results = []
bot2_results = []
bot3_results = []
bot4_results = []

# play the games
for q in Q_VALUES:
    bot1_wins = 0
    bot2_wins = 0
    bot3_wins = 0
    bot4_wins = 0

    for ship_number in range(num_ships):
        grid = ships[ship_number]
        for game_number in range(games_for_ship):
            # every bot gets the same seed so they all play the same game
            seed = ship_number * 1000 + game_number

            # run_simulation plays the whole game and gives back True if the bot won
            if run_simulation(grid, q, bot1, random.Random(seed)):
                bot1_wins += 1
            if run_simulation(grid, q, bot2, random.Random(seed)):
                bot2_wins += 1
            if run_simulation(grid, q, bot3, random.Random(seed)):
                bot3_wins += 1
            if run_simulation(grid, q, bot4, random.Random(seed)):
                bot4_wins += 1

    # success rate = games won / games played
    bot1_results.append(bot1_wins / total_games)
    bot2_results.append(bot2_wins / total_games)
    bot3_results.append(bot3_wins / total_games)
    bot4_results.append(bot4_wins / total_games)

    print("q =", q, " wins out of", total_games, ":", [bot1_wins, bot2_wins, bot3_wins, bot4_wins])

# save the table
csv_file = open("results.csv", "w")
csv_file.write("q,Bot 1,Bot 2,Bot 3,Bot 4\n")
for i in range(len(Q_VALUES)):
    row = str(Q_VALUES[i])
    row = row + "," + str(bot1_results[i])
    row = row + "," + str(bot2_results[i])
    row = row + "," + str(bot3_results[i])
    row = row + "," + str(bot4_results[i])
    csv_file.write(row + "\n")
csv_file.close()
print("saved results.csv")

