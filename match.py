from card import Age, Race, pool
from random import sample
from functools import reduce

# these are one less than 4 base strength cards.
# This means you can win an age with 2 strong cards and 1 base strength card or with 1 really strong card and 2 base strength cards
STONE_BONUS_THRESHOLD = 11
IRON_BONUS_THRESHOLD = 19


def _deckStrength(deck, oppDeck):
    deckStrengths = map(lambda card: card.calcStrength(deck, oppDeck), deck)
    return sum(deckStrengths)


def _age(age, deck1, deck2):
    agedDeck1 = filter(lambda card: card.age.value <= age.value, deck1)
    agedDeck2 = filter(lambda card: card.age.value <= age.value, deck2)
    return _deckStrength(agedDeck1, agedDeck2) - _deckStrength(agedDeck2, agedDeck1)


def match(deck1, deck2, verbose=False):
    stoneResult = _age(Age.STONE, deck1, deck2)
    stoneBonus = stoneResult
    if verbose:
        print(f'stone result: {stoneResult}')
    if abs(stoneResult) < STONE_BONUS_THRESHOLD:
        stoneBonus = 0
    ironResult = _age(Age.IRON, deck1, deck2) + stoneBonus
    ironBonus = ironResult
    if verbose:
        print(f'iron result: {ironResult}')
    if abs(ironResult) < IRON_BONUS_THRESHOLD:
        ironBonus = 0
    if (ironResult >= 0 and stoneResult >= 0) or (ironResult <= 0 and stoneResult <= 0):
        ironBonus = ironBonus + stoneBonus
    return _age(Age.CRYSTAL, deck1, deck2) + ironBonus


def deck_count(age, deck):
    return reduce(lambda acc, card: acc + (card.age == age), deck, 0)


def deck_summary(deck):
    return f'(stone={deck_count(Age.STONE, deck)},iron={deck_count(Age.IRON, deck)},crystal={deck_count(Age.CRYSTAL, deck)})'


pool = pool()
print(f'Pool:\n{pool}\n')
stoneAgePool = list(filter(lambda card: card.age == Age.STONE, pool))
ironAgePool = list(filter(lambda card: card.age == Age.IRON, pool))
crystalAgePool = list(filter(lambda card: card.age == Age.CRYSTAL, pool))
strongPool = list(filter(lambda card: card.race == Race.BEASTMAN, pool))
weakPool = list(filter(lambda card: card.race != Race.BEASTMAN, pool))

random = sample(pool, 20)
# deck2 = sample(pool, 20)
# deck2 = sample(list(filter(lambda card: card.age != Age.CRYSTAL, pool)), 20)
deck2 = stoneAgePool + sample(ironAgePool, 20 - len(stoneAgePool))
decks = {}
decks['even'] = stoneAgePool[0:7] + ironAgePool[0:7] + crystalAgePool[0:6]
decks['stoneOnly'] = stoneAgePool + stoneAgePool[-5:0]
decks['ironOnly'] = ironAgePool + ironAgePool[-5:0]
decks['crystalOnly'] = crystalAgePool + crystalAgePool[-5:0]
decks['stoneIron'] = stoneAgePool[0:10] + ironAgePool[0:10]
decks['stoneCrystal'] = stoneAgePool[0:10] + crystalAgePool[0:10]
decks['ironCrystal'] = ironAgePool[0:10] + crystalAgePool[0:10]
decks['stoneMostly'] = stoneAgePool + stoneAgePool[-3:0] + ironAgePool[0:2]
decks['stoneThresholdIronMostly'] = stoneAgePool[0:4] + ironAgePool + ironAgePool[-1:0]
decks['stoneThresholdEven'] = stoneAgePool[0:4] + ironAgePool[0:8] + crystalAgePool[0:8]
decks['strong'] = stoneAgePool[0:5] + ironAgePool[0:5] + crystalAgePool[0:10]
for i in range(20 - len(decks)):
    decks[f'rand{i}'] = sample(strongPool, 10) + sample(weakPool, 10)
    print('Random {0}:\n{1}'.format(i, decks[f'rand{i}']))

winPct = []
for name1, deck1 in decks.items():
    print('{0}{1}'.format(name1, deck_summary(deck1)))
    wins = 0
    for name2, deck2 in decks.items():
        m = match(deck1, deck2)
        if m > 0:
            wins += 1
        print(f'{name1} vs {name2}: {m}')
    winPct.append((name1, wins / len(decks) * 100))
print()

winPct = sorted(winPct, key=lambda t: t[1], reverse=True)
for name, pct in winPct:
    print('{0} win%: {1:.0f}'.format(name, pct))

print('\niron only {0}'.format(deck_summary(decks['ironOnly'])))
print('\nstone threshold {0}'.format(deck_summary(decks['stoneThresholdIronMostly'])))

# print(f'Deck1:\n{deck1}')
# print(f'Deck2:\n{deck2}')
# # print('')

# print(f'Deck1{deck_summary(deck1)}')
# print(f'Deck2{deck_summary(deck2)}')

print('\nMatch: {0}'.format(match(decks['ironOnly'], decks['stoneThresholdIronMostly'], True)))
