import copy
from icg.constants import Age, Profession, Race, Phase


def simple_deck_strength(deckMetadata):
    if 'simple' not in deckMetadata:
        simple_match(deckMetadata)
    return (deckMetadata['simple']['total'][0] +
            deckMetadata['simple']['total'][1])


# deckMetadata: {
#     deck,
#     base: {
#         cardId: { copy of card },
#         count: {
#             Race.UNDEAD: 0,
#             Age.CRYSTAL: 0,
#             Profession.ALCHEMIST: 0,
#         },
#         total: [0, 0]
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
        'total': [0, 0]
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


def base_metadata():
    return copy.deepcopy(_baseMetadata)


def simple_match(deckMetadata):
    fakeOpponent = copy.deepcopy(_baseMetadata)
    deckMetadata['cur'] = copy.deepcopy(deckMetadata['base'])
    fakeOpponent['cur'] = copy.deepcopy(fakeOpponent['base'])

    # TODO: exclude interactive cards from simple matches
    _phase(deckMetadata, fakeOpponent, Phase.BEFORE)
    _phase(deckMetadata, fakeOpponent, Phase.EFFECT)
    _phase(deckMetadata, fakeOpponent, Phase.AFTER)
    # result is by definition interactive and therefore
    # we exclude it from simple matches
    # _phase(deckMetadata, fakeOpponent, Phase.RESULT)
    deckMetadata['simple'] = deckMetadata['cur']
    return deckMetadata['simple']


def add_card(deckMetadata, card):
    deckMetadata['base']['count'][card.prof] += 1
    deckMetadata['base']['count'][card.race] += 1
    if card.age is not None:
        deckMetadata['base']['count'][card.age] += 1

    deckMetadata['base']['total'][0] += card.strength[0]
    deckMetadata['base']['total'][1] += card.strength[1]

    for effect in card.effects:
        deckMetadata['interactive'] = deckMetadata['interactive'] or effect.interactive
        deckMetadata[effect.phase]['effects'].append(effect)

    deckMetadata['base'][card.cardId] = copy.deepcopy(card)


def to_metadata(deck):
    deckMetadata = base_metadata()
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
        if 'simple' not in deckMetadata1:
            simple_match(deckMetadata1)
        deckMetadata1['cur']['total'] = deckMetadata1['simple']['total']
        if 'simple' not in deckMetadata2:
            simple_match(deckMetadata2)
        deckMetadata2['cur']['total'] = deckMetadata2['simple']['total']

    ironResult = deckMetadata1['cur']['total'][0] - deckMetadata2['cur']['total'][0]
    ironBonus = 0
    # subtract 3 from the bonus to a minimum of 3
    if ironResult > 0:
        ironBonus = max(ironResult - 4, 0)
    else:
        # (where "subtract" means subtract from the winner which mean add if the opponent won)
        ironBonus = min(ironResult + 4, 0)
    if verbose:
        print(f'iron result: {ironResult}')
    return deckMetadata1['cur']['total'][1] - deckMetadata2['cur']['total'][1] + ironBonus
