import sys
import datetime
from multiprocessing import Pool
from icg import card


def multiSim(idx):
    pool = card.generate_pool()
    stats = {}
    stats['triggers'] = {}
    for c in pool:
        for effect in c.effects:
            stats['triggers'][effect.triggerName] = stats['triggers'].get(effect.triggerName, 0) + 1
    return stats


def combineDictOfInts(d1, d2):
    total = d1.copy()
    for key, value in d2.items():
        total[key] = total.get(key, 0) + value
    return total


startTime = datetime.datetime.now()
effects = {}
sims = 10
try:
    sims = int(sys.argv[1])
    print(f'simulating {sims} times')
except (IndexError, ValueError):
    print('simulating 10 times')


if sims == 1:
    verbose = True
pool = Pool()

for simStats in pool.imap_unordered(multiSim, range(sims)):
    effects = combineDictOfInts(effects, simStats['triggers'])

effectPct = []
# triggerWeights = {tt.name: tt.weight for tt in card.triggerTypes}
for effectName, count in effects.items():
    effectPct.append((effectName, count / sims))
effectPct = sorted(effectPct, key=lambda t: t[1], reverse=True)

print()
for name, pct in effectPct:
    print('{0} trigger ratio: {1:.2f}'.format(name, pct))
