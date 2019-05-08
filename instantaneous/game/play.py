import shutil
from functools import reduce
from textwrap import wrap
from instantaneous.game.constants import Mod, Race, Phase, USEFUL_PROFS, DECK_SIZE
from instantaneous.game.card import generate_pool
from instantaneous.game.match import match, to_metadata, simple_deck_strength
from instantaneous.game import ai
from instantaneous.proto import cardpool_pb2

box = {
    'h': '─', 'v': '│',
    'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
    'lb': '├', 'rb': '┤', 'tb': '┬', 'bb': '┴',
    'cross': '┼'
}
cardInnerWidth = 12
cardInnerHeight = 8


def in_card(thing, fill=' ', capitalize=True):
    thing = getattr(thing, 'name', thing)
    line = str(thing)[:cardInnerWidth].ljust(cardInnerWidth, fill)
    if capitalize:
        return line.lower().capitalize()
    return line


def add_detail_to_card(cardDispArr, detail, capitalize=True):
    if len(cardDispArr) == 0:
        cardDispArr.append(in_card(detail, box['h'], capitalize) + box['tb'])
    elif len(cardDispArr) < cardInnerHeight + 1:
        cardDispArr.append(in_card(detail, capitalize=capitalize) + box['v'])


def add_multiline_detail_to_card(cardDispArr, detail, capitalize=True):
    detailArr = wrap(detail, cardInnerWidth)
    for subdetail in detailArr:
        add_detail_to_card(cardDispArr, subdetail, capitalize=capitalize)


def init_card_row():
    cardRow = [box['tl']]
    cardRow.extend(box['v'] * cardInnerHeight)
    cardRow.append(box['bl'])
    return cardRow


def finish_card_row(cardRow):
    cardRow[0] = cardRow[0][:-1] + box['tr']
    cardRow[-1] = cardRow[-1][:-1] + box['br']


# each cardRow is an cardInnerHeight+2 size array of strings representing a row of cards
def finish_card(cardRows, cardDispArr):
    columns = shutil.get_terminal_size()[0]
    cardRow = cardRows[-1]
    if len(cardDispArr) < cardInnerHeight + 1:
        cardDispArr = cardDispArr + ([' ' * cardInnerWidth + box['v']] * (cardInnerHeight + 1 - len(cardDispArr)))
    cardDispArr.append(box['h'] * cardInnerWidth + box['bb'])
    for i, cardDispStr in enumerate(cardDispArr):
        cardRow[i] = cardRow[i] + cardDispStr
    if len(cardRow[0]) + cardInnerWidth + 1 > columns:
        finish_card_row(cardRow)
        cardRows.append(init_card_row())


def display_cards(cards):
    cardDispArr = []
    cardRows = [init_card_row()]
    for i, card in enumerate(cards):
        add_detail_to_card(cardDispArr, card.cardId)
        add_detail_to_card(cardDispArr, '/'.join(map(str, card.strength)))
        add_detail_to_card(cardDispArr, card.age)
        add_detail_to_card(cardDispArr, card.prof)
        add_detail_to_card(cardDispArr, card.race)
        add_detail_to_card(cardDispArr, '')
        add_multiline_detail_to_card(cardDispArr, card.desc, capitalize=False)
        finish_card(cardRows, cardDispArr)
        cardDispArr = []
    if len(cardRows[-1][0]) == 1:
        cardRows = cardRows[:-1]
    if len(cardRows) > 0:
        finish_card_row(cardRows[-1])
    for cardRow in cardRows:
        for cardStr in cardRow:
            print(cardStr)


def mod_count(mod, pool):
    return reduce(lambda acc, card: acc + (card.mod == mod), pool, 0)


# TODO: convert to effect breakdown?
def mod_breakdown(pool):
    return f'(strong={mod_count(Mod.STRONG, pool)};easy={mod_count(Mod.EASY_MATCHING_SYNERGY, pool) + mod_count(Mod.EASY_NONMATCHING_SYNERGY, pool)})'


def play(yourDeckProto, pool):
    yourDeck = []
    for deckCardId in yourDeckProto.card_ids:
        for card in pool:
            if card.cardId == deckCardId:
                yourDeck.append(card)
    if len(yourDeck) != DECK_SIZE:
        raise ValueError("Your deck is the wrong size")
    display_cards(yourDeck)
    decks = generate_ai_decks(pool)
    decks['YOU'] = to_metadata(yourDeck)

    (wins, gamesPlayed, stats) = run_matches(decks, verbose=True)
    result = cardpool_pb2.DeckResult()
    result.wins = wins['YOU']
    # right now, a tie is a loss
    result.losses = gamesPlayed - wins['YOU']
    result.win_rate = wins['YOU'] / gamesPlayed
    rank = 1
    winner = 'YOU'
    mostWins = wins['YOU']
    for enemy, enemyWins in wins.items():
        if enemyWins > wins['YOU']:
            rank = rank + 1
        if enemyWins > mostWins:
            # there may be multiple tied but we assume that is not important to us here
            winner = enemy
            mostWins = enemyWins

    result.rank = rank
    # double check this math
    result.percentile = (len(wins) - rank + 1) / len(wins)
    simple_deck_strength(decks['YOU'])
    result.simple_iron = decks['YOU']['simple']['total'][0]
    result.simple_crystal = decks['YOU']['simple']['total'][1]

    simple_deck_strength(decks[winner])
    result.simple_iron_winner = decks[winner]['simple']['total'][0]
    result.simple_crystal_winner = decks[winner]['simple']['total'][1]
    return result


def run_matches(decks, verbose=False):
    wins = {}

    deckKeys = list(decks.keys())
    for i in range(len(deckKeys) - 1):
        name1 = deckKeys[i]
        deck1 = decks[name1]
        wins[name1] = wins.get(name1, 0)
        for j in range(i + 1, len(deckKeys)):
            name2 = deckKeys[j]
            deck2 = decks[name2]
            wins[name2] = wins.get(name2, 0)
            m = match(deck1, deck2)
            if m > 0:
                wins[name1] = wins[name1] + 1
            if m < 0:
                wins[name2] = wins[name2] + 1
            if name1 == 'YOU':
                print(f'{name1} vs {name2}: {m}')

    # gamesPlayed is the number of games played by each deck
    gamesPlayed = len(deckKeys) - 1
    effects = {}
    bestDeck = deckKeys[0]
    for name, deck in decks.items():
        if wins[name] > wins[bestDeck]:
            bestDeck = name
        if verbose:
            # TODO: fix this once I fix deck summary
            # print('{0}{1}'.format(name1, deck_summary(deck1)))
            simpleStr = simple_deck_strength(deck)
            print('{0} {1} {2}'.format(name, deck['simple']['total'], simpleStr))
    for p in Phase:
        for effect in decks[bestDeck][p]['effects']:
            effects[effect.name] = effects.get(effect.name, 0)
            effects[effect.name] = effects[effect.name] + 1

    stats = {'effects': effects}
    return (wins, gamesPlayed, stats)


def generate_ai_decks(pool, monte=False):
    decks = {}
    decks['even'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.EVEN)])
    decks['ironOnly'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.IRON)])
    decks['crystalOnly'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.CRYSTAL)])
    decks['maxHard'] = ai.build_deck(pool, [ai.max_hard_synergy_strat()])
    decks['ironMaxHard'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.IRON), ai.max_hard_synergy_strat()])
    decks['maxHardIron'] = ai.build_deck(pool, [ai.max_hard_synergy_strat(), ai.breakdown_strat(ai.Breakdown.IRON)])
    decks['counterMaxHard'] = ai.build_deck(pool, [ai.counter_max_hard_strat()])
    for race in Race:
        decks[f'{race.name.lower()}HardSynergy'] = ai.build_deck(pool, [ai.hard_synergy_strat(race)])
    for prof in USEFUL_PROFS:
        decks[f'{prof.name.lower()}HardSynergy'] = ai.build_deck(pool, [ai.hard_synergy_strat(prof)])

    decks['strongIron'] = ai.build_deck(pool, [ai.strong_strat(), ai.breakdown_strat(ai.Breakdown.IRON)])
    decks['ironLopsided'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.IRON),
        ai.strong_strat(),
        ai.lopsided_fill_strat(10),
        ai.easy_synergy_strat()
    ])
    decks['lopsided'] = ai.build_deck(pool, [
        ai.strong_strat(),
        ai.lopsided_fill_strat(10),
        ai.easy_synergy_strat()
    ])
    decks['4iron'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.IRON),
        ai.trigger_strat('defender'),
        ai.trigger_strat('close_defender'),
        ai.fill_to_strat(4),
        ai.breakdown_strat(ai.Breakdown.CRYSTAL),
        ai.trigger_strat('defender'),
        ai.trigger_strat('close_defender')
    ])
    decks['8Iron'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.IRON),
        ai.trigger_strat('close_defender'),
        ai.fill_to_strat(8),
        ai.breakdown_strat(ai.Breakdown.CRYSTAL),
        ai.trigger_strat('close_defender')
    ])
    decks['12Iron'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.IRON),
        ai.trigger_strat('attacker'),
        ai.fill_to_strat(12),
        ai.breakdown_strat(ai.Breakdown.CRYSTAL),
        ai.trigger_strat('attacker')
    ])

    decks['strong'] = ai.build_deck(pool, [])
    decks['specialStrong'] = ai.build_deck(pool, [ai.special_strat()])

    for i in range(3):
        decks[f'rand{i}'] = ai.random_good_strategy(pool)

    # convert ai decks to deckMetadata format
    decks = {k: to_metadata(v) for k, v in decks.items()}

    # the following ai return deckMetadata directly

    # Monte Carlo is super slow compared to other ai so they are disabled unless running simulations
    # or 6000 rounds (around 8 seconds) seems to be the right number for best results
    if monte:
        decks['monteCarlo'] = ai.monte_carlo_deck(pool, iterationLimit=6000)
        # decks['monteCarlo'] = ai.monte_carlo_deck(pool, timeLimit=8000)

    return decks


def simulate(verbose=False, monte=False):
    pool = generate_pool()
    if verbose:
        # this is perhaps TOO verbose
        # display_cards(pool)
        print(mod_breakdown(pool))
    decks = generate_ai_decks(pool)
    return run_matches(decks, verbose=verbose)
