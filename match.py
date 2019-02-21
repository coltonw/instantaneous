from functools import reduce
from card import Age, Mod

# these are one less than 4 base strength cards.
# This means you can win an age with 2 strong cards and 1 base strength card or with 1 really strong card and 2 base strength cards
STONE_BONUS_THRESHOLD = 11
IRON_BONUS_THRESHOLD = 19
DECK_SIZE = 20


def _deck_strength(ageIdx, deck, oppDeck):
    deckStrengths = map(lambda card: card.calc_strength(ageIdx, deck, oppDeck), deck)
    return sum(deckStrengths)


def _age(ageIdx, deck1, deck2):
    return _deck_strength(ageIdx, deck1, deck2) - _deck_strength(ageIdx, deck2, deck1)


def match(deck1, deck2, verbose=False):
    stoneResult = _age(0, deck1, deck2)
    stoneBonus = stoneResult
    if verbose:
        print(f'stone result: {stoneResult}')
    if abs(stoneResult) < STONE_BONUS_THRESHOLD:
        stoneBonus = 0
    ironResult = _age(1, deck1, deck2) + stoneBonus
    ironBonus = ironResult
    if verbose:
        print(f'iron result: {ironResult}')
    if abs(ironResult) < IRON_BONUS_THRESHOLD:
        ironBonus = 0
    if (ironResult >= 0 and stoneResult >= 0) or (ironResult <= 0 and stoneResult <= 0):
        ironBonus = ironBonus + stoneBonus
    return _age(2, deck1, deck2) + ironBonus


def deck_count(age, deck, strong):
    if strong:
        return reduce(lambda acc, card: acc + (card.age == age and card.mod == Mod.STRONG), deck, 0)
    return reduce(lambda acc, card: acc + (card.age == age and card.mod != Mod.STRONG), deck, 0)


def deck_summary(deck):
    return f'(stone={deck_count(Age.STONE, deck, True)}s,{deck_count(Age.STONE, deck, False)}w;iron={deck_count(Age.IRON, deck, True)}s,{deck_count(Age.IRON, deck, False)}w;crystal={deck_count(Age.CRYSTAL, deck, True)}s,{deck_count(Age.CRYSTAL, deck, False)}w)'
