import collections
from random import sample, shuffle
from card import Age, Mod, Profession, HARD_PROF_SYNERGY_THRESHOLD, HARD_RACE_SYNERGY_THRESHOLD
from match import DECK_SIZE


def deck_sample(deck, samplePool, sampleSize=DECK_SIZE):
    result = sample(samplePool, max(min(sampleSize, DECK_SIZE - len(deck), len(samplePool)), 0))
    return deck + result


# this is an arbitrary card strength value used for sorting
def get_card_relative_strength(card):
    if card.mod == Mod.STRONG:
        return 3
    if card.mod == Mod.EASY_MATCHING_SYNERGY or card.mod == Mod.EASY_NONMATCHING_SYNERGY:
        return 2
    elif card.mod == Mod.WEAK or card.mod == Mod.HARD_MATCHING_SYNERGY or card.mod == Mod.HARD_NONMATCHING_SYNERGY:
        return -1
    elif card.mod != Mod.NORMAL:
        return 1
    return 0


def sort_by_strength(basePool):
    return sorted(basePool, key=get_card_relative_strength, reverse=True)


def get_age_pools(basePool):
    pool = basePool[:]
    shuffle(pool)
    pool = sort_by_strength(pool)
    stone = [card for card in pool if card.age == Age.STONE]
    iron = [card for card in pool if card.age == Age.IRON]
    crystal = [card for card in pool if card.age == Age.CRYSTAL]
    return (stone, iron, crystal)


def finish_deck(basePool, deckMap):
    # TODO: add deck breakdowns to this
    pool = basePool[:]
    shuffle(pool)
    pool = sort_by_strength(pool)
    if not isinstance(deckMap, collections.Mapping):
        deckMap = {card.cardId: card for card in deckMap}
    for card in pool:
        if len(deckMap) >= DECK_SIZE:
            break
        deckMap[card.cardId] = card
    return list(deckMap.values())[0:20]


def strong(basePool):
    pool = basePool[:]
    strong = [card for card in pool if card.mod == Mod.STRONG]
    deck = deck_sample([], strong)
    if len(deck) < DECK_SIZE:
        weak = [card for card in pool if card.mod != Mod.STRONG]
        deck = deck_sample(deck, weak)
    return deck


def even(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(stone) > i:
            deck = deck + [stone[i]]
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(crystal) > i:
            deck = deck + [crystal[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20] # rather than do this over and over, we should have a fill deck function that caps off the deck and then fills it with other strong stuff.
    return deck


def stone_iron(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(stone) > i:
            deck = deck + [stone[i]]
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck


def iron_crystal(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(crystal) > i:
            deck = deck + [crystal[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck


def stone_crystal(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(stone) > i:
            deck = deck + [stone[i]]
        if len(crystal) > i:
            deck = deck + [crystal[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck


def stone(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    if len(stone) >= DECK_SIZE:
        return stone[0:20]
    return finish_deck(basePool, stone)


def iron(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    if len(iron) >= DECK_SIZE:
        return iron[0:20]
    return finish_deck(basePool, iron)


def crystal(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    if len(crystal) >= DECK_SIZE:
        return crystal[0:20]
    return finish_deck(basePool, crystal)


def low_stone(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(stone) > i and i < 4:
            deck = deck + [stone[i]]
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(crystal) > i:
            deck = deck + [crystal[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck


def fill_by_synergy(pool, deckMap, synergy, cardsNeeded):
    for card in deckMap.values():
        if card.race == synergy or card.prof == synergy:
            cardsNeeded = cardsNeeded - 1
    sortedPool = sort_by_strength(pool)
    for card in sortedPool:
        if cardsNeeded <= 0:
            break
        if card.race == synergy or card.prof == synergy:
            deckMap[card.cardId] = card
            cardsNeeded = cardsNeeded - 1
    return deckMap


def hard_synergy(basePool, synergy):
    pool = basePool[:]
    deckMap = {}
    for card in pool:
        if (card.mod == Mod.HARD_MATCHING_SYNERGY or card.mod == Mod.HARD_NONMATCHING_SYNERGY) and card.synergy == synergy:
            deckMap[card.cardId] = card
    # print(synergy.name, len(deckMap))
    cardsNeeded = HARD_PROF_SYNERGY_THRESHOLD if isinstance(synergy, Profession) else HARD_RACE_SYNERGY_THRESHOLD
    deckMap = fill_by_synergy(pool, deckMap, synergy, cardsNeeded)
    return finish_deck(pool, deckMap)


def max_hard_synergy(basePool):
    pool = basePool[:]
    hardSynergies = {}
    for card in pool:
        if card.mod == Mod.HARD_NONMATCHING_SYNERGY or card.mod == Mod.HARD_NONMATCHING_SYNERGY:
            hardSynergies.setdefault(card.synergy, {}).update({card.cardId: card})
    maxSynergy = None
    maxSynergyCardDict = {}
    for synergy, cardDict in hardSynergies.items():
        if len(cardDict) > len(maxSynergyCardDict):
            maxSynergy = synergy
            maxSynergyCardDict = cardDict
    # print(maxSynergy.name, len(maxSynergyCardDict))
    deckMap = maxSynergyCardDict
    cardsNeeded = HARD_PROF_SYNERGY_THRESHOLD if isinstance(maxSynergy, Profession) else HARD_RACE_SYNERGY_THRESHOLD
    deckMap = fill_by_synergy(pool, maxSynergyCardDict, maxSynergy, cardsNeeded)
    return finish_deck(pool, deckMap)



# TODO: I want to change these functions to be partial strategies so that multiple can be combined in one deck.
# from email to Jesse:  the "balance" strategies like some stone lots of iron or half stone half iron may need
# to affect other strategies.  Like half stone and half iron but you want strong first within that balance but
# maybe you want all strong no matter what and then after that you want to be even between stone and iron.
