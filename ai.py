import collections
from enum import Flag, auto
from random import choices, sample, shuffle
from card import Age, Mod, Profession, EASY_PROF_SYNERGY_THRESHOLD, EASY_RACE_SYNERGY_THRESHOLD, HARD_PROF_SYNERGY_THRESHOLD, HARD_RACE_SYNERGY_THRESHOLD
from match import DECK_SIZE


class Breakdown(Flag):
    STONE = auto()
    IRON = auto()
    CRYSTAL = auto()
    STONE_IRON = STONE | IRON
    STONE_CRYSTAL = STONE | CRYSTAL
    IRON_CRYSTAL = IRON | CRYSTAL
    EVEN = STONE | IRON | CRYSTAL


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


def age_breakdown(cards):
    cards = sort_by_strength(cards)
    stone = [card for card in cards if card.age == Age.STONE]
    iron = [card for card in cards if card.age == Age.IRON]
    crystal = [card for card in cards if card.age == Age.CRYSTAL]
    return (stone, iron, crystal)


def get_age_pools(basePool):
    pool = basePool[:]
    shuffle(pool)
    return age_breakdown(pool)


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
    # dict keyed by synergy of dicts of cards keyed by cardId
    hardSynergies = {}
    for card in pool:
        if card.mod == Mod.HARD_MATCHING_SYNERGY or card.mod == Mod.HARD_NONMATCHING_SYNERGY:
            hardSynergy = hardSynergies.get(card.synergy, {})
            hardSynergy[card.cardId] = card
            hardSynergies[card.synergy] = hardSynergy
    maxSynergy = None
    maxSynergyCardDict = {}
    for synergy, cardDict in hardSynergies.items():
        if len(cardDict) > len(maxSynergyCardDict):
            maxSynergy = synergy
            maxSynergyCardDict = cardDict
    # print(maxSynergy.name, len(maxSynergyCardDict), maxSynergyCardDict)
    deckMap = maxSynergyCardDict
    cardsNeeded = HARD_PROF_SYNERGY_THRESHOLD if isinstance(maxSynergy, Profession) else HARD_RACE_SYNERGY_THRESHOLD
    deckMap = fill_by_synergy(pool, maxSynergyCardDict, maxSynergy, cardsNeeded)
    return finish_deck(pool, deckMap)


# TODO: I want to change these functions to be partial strategies so that multiple can be combined in one deck.
# from email to Jesse:  the "balance" strategies like some stone lots of iron or half stone half iron may need
# to affect other strategies.  Like half stone and half iron but you want strong first within that balance but
# maybe you want all strong no matter what and then after that you want to be even between stone and iron.
# TODO: convert all the above into the below


def _add_card(card, deckMap, ageCounts):
    if card.cardId not in deckMap:
        ageCounts[card.age] = ageCounts.get(card.age, 0) + 1
        deckMap.update({card.cardId: card})
    return (deckMap, ageCounts)


def _add_cards(pool, deckMap, ageCounts):
    for card in pool:
        if len(deckMap) >= DECK_SIZE:
            break
        (deckMap, ageCounts) = _add_card(card, deckMap, ageCounts)
    return (deckMap, ageCounts)


def _add_cards_with_breakdown(pool, deckMap, breakdown, ageCounts):
    (stone, iron, crystal) = age_breakdown(pool)
    startingAgeCounts = ageCounts.copy()
    for i in range(DECK_SIZE):
        if len(deckMap) >= DECK_SIZE:
            return (deckMap, ageCounts)
        needsStone = Breakdown.STONE in breakdown
        stoneIdx = i - startingAgeCounts.get(Age.STONE, 0)
        if len(stone) > stoneIdx and stoneIdx >= 0 and needsStone:
            if stone[stoneIdx].cardId not in deckMap:
                deckMap.update({stone[stoneIdx].cardId: stone[stoneIdx]})
                ageCounts[Age.STONE] = ageCounts.get(Age.STONE, 0) + 1
        if len(deckMap) >= DECK_SIZE:
            return (deckMap, ageCounts)
        needsIron = Breakdown.IRON in breakdown
        ironIdx = i - startingAgeCounts.get(Age.IRON, 0)
        if len(iron) > ironIdx and ironIdx >= 0 and needsIron:
            if iron[ironIdx].cardId not in deckMap:
                deckMap.update({iron[ironIdx].cardId: iron[ironIdx]})
                ageCounts[Age.IRON] = ageCounts.get(Age.IRON, 0) + 1
        if len(deckMap) >= DECK_SIZE:
            return (deckMap, ageCounts)
        needsCrystal = Breakdown.CRYSTAL in breakdown
        crystalIdx = i - startingAgeCounts.get(Age.CRYSTAL, 0)
        if len(crystal) > crystalIdx and crystalIdx >= 0 and needsCrystal:
            if crystal[crystalIdx].cardId not in deckMap:
                deckMap.update({crystal[crystalIdx].cardId: crystal[crystalIdx]})
                ageCounts[Age.CRYSTAL] = ageCounts.get(Age.CRYSTAL, 0) + 1
    return (deckMap, ageCounts)


def _fill_to_count(pool, deckMap, ageCounts, count):
    total_needed = len(deckMap) + count
    for card in pool:
        if len(deckMap) >= total_needed:
            break
        (deckMap, ageCounts) = _add_card(card, deckMap, ageCounts)
    # TODO: throw error if you don't reach count. Requires error handling first
    return (deckMap, ageCounts)


def _apply_filter_strat(pool, deckMap, test, breakdown, ageCounts, breakout=False, count=None):
    # TODO: breakout means you have to fill in the count even if it no longer matches the breakdown
    # if breakout is true and count is None, it means just add all matching cards
    # we need to add a "max" to the two add cards functions to support count and breakout
    matching = [card for card in pool if test(card)]
    # startingDeckSize = len(deckMap)
    if breakdown is None:
        (deckMap, ageCounts) = _add_cards(matching, deckMap, ageCounts)
    else:
        (deckMap, ageCounts) = _add_cards_with_breakdown(matching, deckMap, breakdown, ageCounts)
    return (deckMap, breakdown, ageCounts)


##############
# STRATEGIES #
##############


def breakdown_strat(newBreakdown):
    def strat(pool, deckMap, oldBreakdown, ageCounts):
        return (deckMap, newBreakdown, ageCounts)
    return strat


def strong_strat(breakout=False):
    def strat(pool, deckMap, breakdown, ageCounts):
        return _apply_filter_strat(pool, deckMap, lambda c: c.mod == Mod.STRONG, breakdown, ageCounts, breakout=breakout)
    return strat


def easy_synergy_strat(breakout=False):
    # this strat only makes sense as a follow-up strategy after others
    def strat(pool, deckMap, breakdown, ageCounts):
        synergies = {}
        for c in deckMap:
            synergies[c.race] = synergies.get(c.race, 0) + 1
            synergies[c.prof] = synergies.get(c.prof, 0) + 1
        for card in pool:
            if card.mod == Mod.EASY_MATCHING_SYNERGY or card.mod == Mod.EASY_NONMATCHING_SYNERGY:
                minCount = EASY_PROF_SYNERGY_THRESHOLD if isinstance(card.synergy, Profession) else EASY_RACE_SYNERGY_THRESHOLD
                if synergies.get(card.synergy, 0) >= minCount:
                    (deckMap, ageCounts) = _add_card(card, deckMap, ageCounts)
        return (deckMap, breakdown, ageCounts)
    return strat


# END STRATEGIES


def _finish_breakdown(pool, deckMap, breakdown, ageCounts):
    (deckMap, ageCount) = _add_cards_with_breakdown(pool, deckMap, breakdown, ageCounts)
    return deckMap


def build_deck(basePool, strategies):
    pool = basePool[:]
    deckMap = {}
    breakdown = None
    ageCounts = {}
    for strategy in strategies:
        (deckMap, breakdown, ageCounts) = strategy(pool, deckMap, breakdown, ageCounts)
        if len(deckMap) >= DECK_SIZE:
            break
    if breakdown is not None:
        deckMap = _finish_breakdown(pool, deckMap, breakdown, ageCounts)
    return finish_deck(pool, deckMap)


def random_strategy(basePool):
    strats = []
    breakdown = choices([Breakdown.STONE, Breakdown.STONE_IRON, Breakdown.EVEN, None], weights= [1, 2, 3, 6])[0]

    if breakdown is not None:
        strats.append(breakdown_strat(breakdown))
    strats.append(strong_strat())
    shuffle(strats)
    return build_deck(basePool, strats)
