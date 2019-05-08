import collections
from enum import Flag, auto
from random import choices, randrange, sample, shuffle
from .constants import (Age, Mod, Profession, Race, EASY_PROF_SYNERGY_THRESHOLD, EASY_RACE_SYNERGY_THRESHOLD,
                        HARD_PROF_SYNERGY_THRESHOLD, HARD_RACE_SYNERGY_THRESHOLD, BASE_STRENGTH, DECK_SIZE)
from .match import simple_deck_strength, to_metadata
from .montecarlo import mcts


class Breakdown(Flag):
    IRON = auto()
    CRYSTAL = auto()
    EVEN = IRON | CRYSTAL


def deck_sample(deck, samplePool, sampleSize=DECK_SIZE):
    result = sample(samplePool, max(min(sampleSize, DECK_SIZE - len(deck), len(samplePool)), 0))
    return deck + result


def is_weak(card):
    return card.age is not None and card.strength[1] < BASE_STRENGTH[card.age][1]


# this is an arbitrary card strength value used for sorting
def _get_card_relative_strength(card):
    if card.mod == Mod.STRONG:
        return 2
    elif is_weak(card):
        return -1
    elif card.mod != Mod.NORMAL:
        return 1
    return 0


def sort_by_strength(basePool):
    return sorted(basePool, key=_get_card_relative_strength, reverse=True)


def age_breakdown(cards):
    cards = sort_by_strength(cards)
    iron = [card for card in cards if card.age == Age.IRON]
    crystal = [card for card in cards if card.age == Age.CRYSTAL]
    return (iron, crystal)


def get_age_pools(basePool):
    pool = basePool[:]
    shuffle(pool)
    return age_breakdown(pool)


def finish_deck(basePool, deckMap):
    pool = basePool[:]
    shuffle(pool)
    pool = sort_by_strength(pool)
    if not isinstance(deckMap, collections.Mapping):
        deckMap = {card.cardId: card for card in deckMap}
    for card in pool:
        if len(deckMap) >= DECK_SIZE:
            break
        deckMap[card.cardId] = card
    return list(deckMap.values())[0:DECK_SIZE]


def _add_card(card, deckMap, ageCounts):
    if card.cardId not in deckMap:
        ageCounts[card.age] = ageCounts.get(card.age, 0) + 1
        deckMap.update({card.cardId: card})
    return (deckMap, ageCounts)


def _add_cards(pool, deckMap, ageCounts, count=None):
    startLen = len(deckMap)
    pool = sort_by_strength(pool)
    for card in pool:
        if len(deckMap) >= DECK_SIZE or (count is not None and len(deckMap) - startLen >= count):
            break
        (deckMap, ageCounts) = _add_card(card, deckMap, ageCounts)
    return (deckMap, ageCounts)


def _add_cards_with_breakdown(pool, deckMap, breakdown, ageCounts, count=None):
    (iron, crystal) = age_breakdown(pool)
    startingAgeCounts = ageCounts.copy()
    cardsAdded = 0
    for i in range(DECK_SIZE):
        if len(deckMap) >= DECK_SIZE or (count is not None and cardsAdded >= count):
            return (deckMap, ageCounts)
        needsIron = Breakdown.IRON in breakdown
        ironIdx = i - startingAgeCounts.get(Age.IRON, 0)
        if len(iron) > ironIdx and ironIdx >= 0 and needsIron:
            if iron[ironIdx].cardId not in deckMap:
                deckMap.update({iron[ironIdx].cardId: iron[ironIdx]})
                ageCounts[Age.IRON] = ageCounts.get(Age.IRON, 0) + 1
                cardsAdded = cardsAdded + 1
        if len(deckMap) >= DECK_SIZE or (count is not None and cardsAdded >= count):
            return (deckMap, ageCounts)
        needsCrystal = Breakdown.CRYSTAL in breakdown
        crystalIdx = i - startingAgeCounts.get(Age.CRYSTAL, 0)
        if len(crystal) > crystalIdx and crystalIdx >= 0 and needsCrystal:
            if crystal[crystalIdx].cardId not in deckMap:
                deckMap.update({crystal[crystalIdx].cardId: crystal[crystalIdx]})
                ageCounts[Age.CRYSTAL] = ageCounts.get(Age.CRYSTAL, 0) + 1
                cardsAdded = cardsAdded + 1
    return (deckMap, ageCounts)


def _apply_filter_strat(pool, deckMap, test, breakdown, ageCounts, breakout=False, count=None):
    # breakout means you have to fill in the count even if it no longer matches the breakdown
    # if breakout is true and count is None, it means just add all matching cards
    # if count is not None and breakout is False count is a max to add
    matching = [card for card in pool if test(card)]
    startingSize = len(deckMap)
    if breakdown is None:
        (deckMap, ageCounts) = _add_cards(matching, deckMap, ageCounts, count)
    else:
        (deckMap, ageCounts) = _add_cards_with_breakdown(matching, deckMap, breakdown, ageCounts, count)
    cardsAdded = len(deckMap) - startingSize
    if breakout and count is None:
        if count is None:
            _add_cards(matching, deckMap, ageCounts)
        elif cardsAdded < count:
            _add_cards(matching, deckMap, ageCounts, count - cardsAdded)
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


def special_strat():
    def strat(pool, deckMap, breakdown, ageCounts):
        return _apply_filter_strat(pool, deckMap, lambda c: c.mod == Mod.SPECIAL, breakdown, ageCounts, breakout=True)
    return strat


def trigger_strat(triggerName):
    def strat(pool, deckMap, breakdown, ageCounts):
        return _apply_filter_strat(pool, deckMap, lambda c: len(c.effects) > 0 and c.effects[0].triggerName == triggerName, breakdown, ageCounts)
    return strat


def easy_synergy_strat(breakout=False):
    # this strat only makes sense as a follow-up strategy after others
    def strat(pool, deckMap, breakdown, ageCounts):
        synergies = {}
        for c in deckMap.values():
            synergies[c.race] = synergies.get(c.race, 0) + 1
            synergies[c.prof] = synergies.get(c.prof, 0) + 1
        matching = []
        for card in pool:
            if card.mod == Mod.EASY_MATCHING_SYNERGY or card.mod == Mod.EASY_NONMATCHING_SYNERGY:
                minCount = EASY_PROF_SYNERGY_THRESHOLD if isinstance(card.synergy, Profession) else EASY_RACE_SYNERGY_THRESHOLD
                if synergies.get(card.synergy, 0) >= minCount:
                    matching.append(card)
        if breakdown is None:
            (deckMap, ageCounts) = _add_cards(matching, deckMap, ageCounts)
        else:
            (deckMap, ageCounts) = _add_cards_with_breakdown(matching, deckMap, breakdown, ageCounts)
        return (deckMap, breakdown, ageCounts)
    return strat


def hard_synergy_strat(synergy):
    def strat(pool, deckMap, breakdown, ageCounts):
        matching = {}
        for card in pool:
            if (card.mod == Mod.HARD_MATCHING_SYNERGY or card.mod == Mod.HARD_NONMATCHING_SYNERGY) and (card.race == synergy or card.prof == synergy):
                matching[card.cardId] = card
        if len(matching) > 0:
            deckMap.update(matching)
            def synergyTest(c):
                return c.race == synergy or c.prof == synergy
            cardsMatching = sum([1 for c in deckMap.values() if synergyTest(c)])
            cardsNeeded = HARD_PROF_SYNERGY_THRESHOLD if isinstance(synergy, Profession) else HARD_RACE_SYNERGY_THRESHOLD
            return _apply_filter_strat(pool, deckMap, synergyTest, breakdown, ageCounts,
                                       breakout=True, count=cardsNeeded - cardsMatching)
        return (deckMap, breakdown, ageCounts)
    return strat


def _get_hard_synergies(pool):
    hardSynergies = {}
    for card in pool:
        if card.mod == Mod.HARD_MATCHING_SYNERGY or card.mod == Mod.HARD_NONMATCHING_SYNERGY:
            hardSynergy = hardSynergies.get(card.synergy, {})
            hardSynergy[card.cardId] = card
            hardSynergies[card.synergy] = hardSynergy
    return hardSynergies


def _get_max_synergy(hardSynergies):
    maxSynergy = None
    maxSynergyCardDict = {}
    for synergy, cardDict in hardSynergies.items():
        if len(cardDict) > len(maxSynergyCardDict):
            maxSynergy = synergy
            maxSynergyCardDict = cardDict
    return (maxSynergy, maxSynergyCardDict)


def max_hard_synergy_strat():
    def strat(pool, deckMap, breakdown, ageCounts):
        # dict keyed by synergy of dicts of cards keyed by cardId
        hardSynergies = _get_hard_synergies(pool)
        (maxSynergy, maxSynergyCardDict) = _get_max_synergy(hardSynergies)
        # print(maxSynergy.name, len(maxSynergyCardDict), maxSynergyCardDict)
        deckMap.update(maxSynergyCardDict)

        def synergyTest(c):
            return c.race == maxSynergy or c.prof == maxSynergy
        cardsMatching = sum([1 for c in deckMap.values() if synergyTest(c)])
        cardsNeeded = HARD_PROF_SYNERGY_THRESHOLD if isinstance(maxSynergy, Profession) else HARD_RACE_SYNERGY_THRESHOLD
        return _apply_filter_strat(pool, deckMap, synergyTest, breakdown, ageCounts,
                                   breakout=True, count=cardsNeeded - cardsMatching)
    return strat


def counter_max_hard_strat():
    def strat(pool, deckMap, breakdown, ageCounts):
        # dict keyed by synergy of dicts of cards keyed by cardId
        hardSynergies = _get_hard_synergies(pool)
        (maxSynergy, maxSynergyCardDict) = _get_max_synergy(hardSynergies)
        # print(maxSynergy.name)

        def counterTest(c):
            return c.synergy == maxSynergy and c.mod == Mod.COUNTER
        return _apply_filter_strat(pool, deckMap, counterTest, breakdown, ageCounts)
    return strat

# gives specific number of cards no matter what
def fill_strat(count):
    def strat(pool, deckMap, breakdown, ageCounts):
        if breakdown is None:
            (deckMap, ageCounts) = _add_cards(pool, deckMap, ageCounts, count)
        else:
            (deckMap, ageCounts) = _add_cards_with_breakdown(pool, deckMap, breakdown, ageCounts, count)
        return (deckMap, breakdown, ageCounts)
    return strat


# fills deck till it has count number of cards
def fill_to_strat(count):
    def strat(pool, deckMap, breakdown, ageCounts):
        numToAdd = max(count - len(deckMap), 0)
        if breakdown is None:
            (deckMap, ageCounts) = _add_cards(pool, deckMap, ageCounts, numToAdd)
        else:
            (deckMap, ageCounts) = _add_cards_with_breakdown(pool, deckMap, breakdown, ageCounts, numToAdd)
        return (deckMap, breakdown, ageCounts)
    return strat


def lopsided_fill_strat(count):
    def strat(pool, deckMap, breakdown, ageCounts):
        raceCounts = {}
        profCounts = {}
        for c in deckMap.values():
            raceCounts[c.race] = raceCounts.get(c.race, 0) + 1
            profCounts[c.prof] = profCounts.get(c.prof, 0) + 1

        races = list(Race)
        shuffle(races)
        races = sorted(races, key=lambda r: raceCounts.get(r, 0))
        races = set(races[0:2])
        profs = list(Profession)
        shuffle(profs)
        profs = sorted(profs, key=lambda p: profCounts.get(p, 0))
        profs = set(profs[0:3])

        def matches(c):
            return c.race in races and c.prof in profs
        return _apply_filter_strat(pool, deckMap, matches, breakdown, ageCounts, count=count)
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


def random_good_strategy(basePool):
    strats = []
    breakdown = choices([Breakdown.IRON, Breakdown.EVEN, None], weights=[1, 2, 3])[0]

    if breakdown is not None:
        strats.append(breakdown_strat(breakdown))
    strats.append(strong_strat())
    shuffle(strats)
    strats = strats + [fill_strat(randrange(4, 10)), easy_synergy_strat()]
    return build_deck(basePool, strats)


class DeckBuildingState():
    def __init__(self, basePool=None, poolMap=None, poolOptions=None, cardIdSet=None):
        if poolMap is not None:
            self.poolMap = poolMap
        elif basePool is not None:
            self.poolMap = {c.cardId: c for c in basePool}
        else:
            raise ValueError('Must have basePool or poolMap')

        if poolOptions is not None:
            self.poolOptions = poolOptions
        else:
            self.poolOptions = set(self.poolMap.keys())

        if cardIdSet is not None:
            self.cardIdSet = cardIdSet
        else:
            self.cardIdSet = set()

    def getPossibleActions(self):
        return tuple(self.poolOptions)

    def takeAction(self, action):
        newCardIdSet = self.cardIdSet | {action}
        newPoolOptions = self.poolOptions - {action}
        return DeckBuildingState(poolMap=self.poolMap, poolOptions=newPoolOptions, cardIdSet=newCardIdSet)

    def isTerminal(self):
        return len(self.cardIdSet) == DECK_SIZE

    def getReward(self):
        # only needed for terminal states
        deck = []
        for cardId in self.cardIdSet:
            deck.append(self.poolMap[cardId])
        self.deckMetadata = to_metadata(deck)
        return simple_deck_strength(self.deckMetadata)

    def __eq__(self, other):
        return self.cardIdSet == other.cardIdSet


def monte_carlo_deck(basePool, iterationLimit=None, timeLimit=None):
    if iterationLimit is None and timeLimit is None:
        iterationLimit = 1000
    treeSearch = mcts(iterationLimit=iterationLimit, timeLimit=timeLimit)
    terminalState = treeSearch.search_terminal_state(DeckBuildingState(basePool=basePool))
    return terminalState.deckMetadata
