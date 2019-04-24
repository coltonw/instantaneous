import sys
from multiprocessing import Pool
from instantaneous.game.play import simulate


verbose = False


def multiSim(idx):
    global verbose
    return simulate({}, 0, verbose=verbose)


def combineWins(wins1, wins2):
    totalWins = wins1.copy()
    for name, w in wins2.items():
        totalWins[name] = totalWins.get(name, 0) + w
    return totalWins


def combineHighestWins(highestWins, wins):
    names = []
    maxWins = 0
    for name, w in wins.items():
        if w == maxWins:
            names.append(name)
        if w > maxWins:
            names = [name]
            maxWins = w
    for name in names:
        highestWins[name] = highestWins.get(name, 0) + 1
    return highestWins


wins = {}
highestWins = {}
gamesPlayed = 0
sims = 10
try:
    sims = int(sys.argv[1])
    print(f'simulating {sims} times')
except (IndexError, ValueError):
    print('simulating 10 times')
if sims == 1:
    verbose = True
pool = Pool()
for simWins, simGamesPlayed in pool.imap_unordered(multiSim, range(sims)):
    wins = combineWins(wins, simWins)
    highestWins = combineHighestWins(highestWins, simWins)
    gamesPlayed += simGamesPlayed


winPct = []
for deckName, wins in wins.items():
    winPct.append((deckName, wins / gamesPlayed * 100))
winPct = sorted(winPct, key=lambda t: t[1], reverse=True)

highestWinPct = []
for deckName, wins in highestWins.items():
    highestWinPct.append((deckName, wins / sims * 100))
highestWinPct = sorted(highestWinPct, key=lambda t: t[1], reverse=True)

print()
for name, pct in winPct:
    print('{0} win%: {1:.0f}'.format(name, pct))
print()
for name, pct in highestWinPct:
    print('{0} best in pool %: {1:.1f}'.format(name, pct))
