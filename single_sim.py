# This file exists purely for profiling since the multiprocessing module
# breaks the profiler
from instantaneous.game.play import simulate

(wins, gamesPlayed, stats) = simulate(verbose=False)

print(wins)
