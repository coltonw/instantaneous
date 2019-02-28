import sys
from multiprocessing import Pool
from card import generate_pool
from play import simulate, display_cards


def multiSim(idx):
    return simulate({}, 0)


def combineWins(wins1, wins2):
    totalWins = wins1.copy()
    for name, w in wins2.items():
        totalWins[name] = totalWins.get(name, 0) + w
    return totalWins


wins = {}
gamesPlayed = 0
sims = 10
try:
    sims = int(sys.argv[1])
    print(f'simulating {sims} times')
except (IndexError, ValueError):
    print('simulating 10 times')
pool = Pool()
for simWins, simGamesPlayed in pool.imap_unordered(multiSim, range(sims)):
    wins = combineWins(wins, simWins)
    gamesPlayed += simGamesPlayed


winPct = []
for deckName, wins in wins.items():
    winPct.append((deckName, wins / gamesPlayed * 100))
winPct = sorted(winPct, key=lambda t: t[1], reverse=True)
print()
for name, pct in winPct:
    print('{0} win%: {1:.0f}'.format(name, pct))