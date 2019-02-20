from functools import reduce
from card import Age, BASE_STRENGTH

# these are one less than 4 base strength cards.
# This means you can win an age with 2 strong cards and 1 base strength card or with 1 really strong card and 2 base strength cards
STONE_BONUS_THRESHOLD = 11
IRON_BONUS_THRESHOLD = 19
DECK_SIZE = 20


def _deck_strength(deck, oppDeck):
    deckStrengths = map(lambda card: card.calcStrength(deck, oppDeck), deck)
    return sum(deckStrengths)


def _age(age, deck1, deck2):
    agedDeck1 = filter(lambda card: card.age.value <= age.value, deck1)
    agedDeck2 = filter(lambda card: card.age.value <= age.value, deck2)
    return _deck_strength(agedDeck1, agedDeck2) - _deck_strength(agedDeck2, agedDeck1)


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


def deck_count(age, deck, strong):
    if strong:
        return reduce(lambda acc, card: acc + (card.age == age and card.strength > BASE_STRENGTH[card.age]), deck, 0)
    return reduce(lambda acc, card: acc + (card.age == age and card.strength <= BASE_STRENGTH[card.age]), deck, 0)


def deck_summary(deck):
    return f'(stone={deck_count(Age.STONE, deck, True)}s,{deck_count(Age.STONE, deck, False)}w;iron={deck_count(Age.IRON, deck, True)}s,{deck_count(Age.IRON, deck, False)}w;crystal={deck_count(Age.CRYSTAL, deck, True)}s,{deck_count(Age.CRYSTAL, deck, False)}w)'
