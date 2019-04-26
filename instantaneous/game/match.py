from functools import reduce
import copy
from instantaneous.game.card import Age, Profession, Race, Mod, Phase

# these are one less than 4 base strength cards.
# This means you can win an age with 2 strong cards and 1 base strength card or with 1 really strong card and 2 base strength cards
STONE_BONUS_THRESHOLD = 11
IRON_BONUS_THRESHOLD = 19
DECK_SIZE = 20


# TODO: apply effects. Monte Carlo is going to suck now sortof
def simple_deck_strength(deckMetadata):
    return deckMetadata['base']['total'][0] * 2 + deckMetadata['base']['total'][1] + deckMetadata['base']['total'][2]


# deckMetadata: {
#     deck,
#     base: {
#         cardId: { copy of card },
#         count: {
#             Race.UNDEAD: 0,
#             Age.CRYSTAL: 0,
#             Profession.ALCHEMIST: 0,
#         },
#         total: [0, 0, 0]
#     },
#     cur:  { same as base...},
#     simple: { same as base...},
#     interactive: False,
#     Phase.BEFORE: {
#         effects,
#     }
# }
_baseMetadata = {
    'deck': [],
    'base': {
        'count': {},
        'total': [0, 0, 0]
    },
    'interactive': False
}
for prof in Profession:
    _baseMetadata['base']['count'][prof] = 0
for race in Race:
    _baseMetadata['base']['count'][race] = 0
for age in Age:
    _baseMetadata['base']['count'][age] = 0
for phase in Phase:
    _baseMetadata[phase] = {'effects': []}


def simple_match(deckMetadata):
    fakeOpponent = copy.deepcopy(_baseMetadata)
    deckMetadata['cur'] = copy.deepcopy(deckMetadata['base'])
    fakeOpponent['cur'] = copy.deepcopy(fakeOpponent['base'])

    _phase(deckMetadata, fakeOpponent, Phase.BEFORE)
    _phase(deckMetadata, fakeOpponent, Phase.EFFECT)
    _phase(deckMetadata, fakeOpponent, Phase.AFTER)
    _phase(deckMetadata, fakeOpponent, Phase.RESULT)
    deckMetadata['simple'] = deckMetadata['cur']
    return deckMetadata['simple']


def add_card(deckMetadata, card):
    deckMetadata['base']['count'][card.prof] += 1
    deckMetadata['base']['count'][card.race] += 1
    if card.age is not None:
        deckMetadata['base']['count'][card.age] += 1

    deckMetadata['base']['total'][0] += card.strength[0]
    deckMetadata['base']['total'][1] += card.strength[1]
    deckMetadata['base']['total'][2] += card.strength[2]

    for effect in card.effects:
        deckMetadata['interactive'] = deckMetadata['interactive'] or effect.interactive
        deckMetadata[effect.phase]['effects'].append(effect)

    deckMetadata['base'][card.cardId] = copy.deepcopy(card)


def to_metadata(deck):
    deckMetadata = copy.deepcopy(_baseMetadata)
    deckMetadata['deck'] = deck
    for card in deck:
        add_card(deckMetadata, card)
    if not deckMetadata['interactive']:
        simple_match(deckMetadata)
    return deckMetadata


def _phase(deckMetadata, oppDeckMetadata, phase):
    effectsToApply = []
    for effect in deckMetadata[phase]['effects']:
        if effect.check(deckMetadata['cur'], oppDeckMetadata['cur']):
            effectsToApply.append(effect)

    oppEffectsToApply = []
    for effect in oppDeckMetadata[phase]['effects']:
        if effect.check(oppDeckMetadata['cur'], deckMetadata['cur']):
            oppEffectsToApply.append(effect)

    # TODO: For certain effects, order could matter here...
    for effect in effectsToApply:
        effect.apply(deckMetadata['cur'], oppDeckMetadata['cur'])
    for effect in oppEffectsToApply:
        effect.apply(oppDeckMetadata['cur'], deckMetadata['cur'])


# Phase 0: "Before card effects" - Card generation and self-destruction
# Phase 1: Normal card effects - Typically synergies and counters based on deck composition
# Phase 2: "After card effects" - Synergies and counters based on strength
# Phase 3: "If winning/losing the age" Synergies based on result
# Despite ages implying a passage of time, effects are calculated one time total, not once per age.
def match(deckMetadata1, deckMetadata2, verbose=False):
    if deckMetadata1['interactive'] or deckMetadata2['interactive']:
        deckMetadata1['cur'] = copy.deepcopy(deckMetadata1['base'])
        deckMetadata2['cur'] = copy.deepcopy(deckMetadata2['base'])

        _phase(deckMetadata1, deckMetadata2, Phase.BEFORE)
        _phase(deckMetadata1, deckMetadata2, Phase.EFFECT)
        _phase(deckMetadata1, deckMetadata2, Phase.AFTER)
        _phase(deckMetadata1, deckMetadata2, Phase.RESULT)
    else:
        deckMetadata1['cur']['total'] = deckMetadata1['simple']['total']
        deckMetadata2['cur']['total'] = deckMetadata2['simple']['total']

    stoneResult = deckMetadata1['cur']['total'][0] - deckMetadata2['cur']['total'][0]
    stoneBonus = stoneResult
    if verbose:
        print(f'stone result: {stoneResult}')
    if abs(stoneResult) < STONE_BONUS_THRESHOLD:
        stoneBonus = 0
    ironResult = deckMetadata1['cur']['total'][1] - deckMetadata2['cur']['total'][1] + stoneBonus
    ironBonus = ironResult
    if verbose:
        print(f'iron result: {ironResult}')
    if abs(ironResult) < IRON_BONUS_THRESHOLD:
        ironBonus = 0
    # You only get the stone bonus in phase three if you also won the iron age
    if (ironResult >= 0 and stoneResult >= 0) or (ironResult <= 0 and stoneResult <= 0):
        ironBonus = ironBonus + stoneBonus
    return deckMetadata1['cur']['total'][2] - deckMetadata2['cur']['total'][2] + ironBonus

# TODO: fix this.  Depends on fixing simple_deck_strength or just adding precalced deck stuff to metadata
# def deck_summary(deckMetadata):
#     return f'(stone={deckMetadata['base']['count'][Age.STONE]},{_deck_strength(0, deck, [])}str;iron={age_count(Age.IRON, deck)},{_deck_strength(1, deck, [])}str;crystal={age_count(Age.CRYSTAL, deck)},{_deck_strength(2, deck, [])}str)'
