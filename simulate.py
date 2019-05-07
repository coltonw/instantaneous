import sys
import datetime
from multiprocessing import Pool
from instantaneous.game.play import simulate
from instantaneous.game import match


verbose = False
monte = False


def multiSim(idx):
    global verbose
    return simulate({}, 0, verbose=verbose, monte=monte)


def combineDictOfInts(d1, d2):
    total = d1.copy()
    for key, value in d2.items():
        total[key] = total.get(key, 0) + value
    return total


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


startTime = datetime.datetime.now()
wins = {}
highestWins = {}
effects = {}
gamesPlayed = 0
sims = 10
try:
    sims = int(sys.argv[1])
    print(f'simulating {sims} times')
except (IndexError, ValueError):
    print('simulating 10 times')

try:
    if sys.argv[2].startswith('m'):
        monte = True
        print(f'including monte')
except (IndexError, ValueError):
    pass

if not monte:
    print('NOT including monte')

if sims == 1:
    verbose = True
pool = Pool()

for simWins, simGamesPlayed, simEffects, _ in pool.imap_unordered(multiSim, range(sims)):
    wins = combineDictOfInts(wins, simWins)
    highestWins = combineHighestWins(highestWins, simWins)
    effects = combineDictOfInts(effects, simEffects)
    gamesPlayed += simGamesPlayed

endTime = datetime.datetime.now()
deltaTime = endTime - startTime
print()
totalMatches = len(wins) * gamesPlayed / 2
print(f'Total matches: {totalMatches:.0f}')
print(f'Total wins: {sum(wins.values())}')
# ~6600 on commit 792114a8
# ~46000 on commit b38b26ae (new game engine plus caching)
print(f'Matches / second: {totalMatches / deltaTime.total_seconds():.0f}')

winPct = []
for deckName, wins in wins.items():
    winPct.append((deckName, wins / gamesPlayed * 100))
winPct = sorted(winPct, key=lambda t: t[1], reverse=True)

highestWinPct = []
for deckName, wins in highestWins.items():
    highestWinPct.append((deckName, wins / sims * 100))
highestWinPct = sorted(highestWinPct, key=lambda t: t[1], reverse=True)

effectPct = []
for effectName, count in effects.items():
    effectPct.append((effectName, count / sims))
effectPct = sorted(effectPct, key=lambda t: t[1], reverse=True)

print()
for name, pct in winPct:
    print('{0} win%: {1:.0f}'.format(name, pct))
print()
for name, pct in highestWinPct:
    print('{0} best in pool %: {1:.1f}'.format(name, pct))
print()
for name, pct in effectPct:
    print('{0} pick ratio: {1:.2f}'.format(name, pct))
