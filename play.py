import shutil
import sys
from textwrap import wrap
from card import generate_pool, Race, Profession
from match import DECK_SIZE, match, deck_summary
import ai

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


# TODO: fix this?
def play():
    pool = generate_pool()
    deckMap = {}
    try:
        # idea: input comma separated ints to enable or negative ints to disable cards in your deck
        while len(deckMap) != DECK_SIZE:
            deckChange = input('?')
            changes = deckChange.split(',')
            for change in changes:
                # cannot remove 0?
                if change.startswith('-'):
                    del deckMap[abs(int(change))]
                else:
                    deckMap[int(change)] = pool[int(change)]
            print(f'{sorted(list(deckMap.keys()))}, len: {len(deckMap)}')
    except ValueError:
        print('Skipping your deck')

# print(f'Pool:\n{pool}\n')
# stoneAgePool = list(filter(lambda card: card.age == Age.STONE, pool))
# ironAgePool = list(filter(lambda card: card.age == Age.IRON, pool))
# crystalAgePool = list(filter(lambda card: card.age == Age.CRYSTAL, pool))
# strongPool = list(filter(lambda card: card.race == Race.BEASTMAN, pool))
# weakPool = list(filter(lambda card: card.race != Race.BEASTMAN, pool))


def simulate(wins, gamesPlayed, yourDeck=None, verbose=False):
    pool = generate_pool()
    if verbose:
        display_cards(pool)
    decks = {}
    if yourDeck and len(yourDeck) == DECK_SIZE:
        decks['YOU'] = yourDeck.values()
        display_cards(decks['YOU'])
    decks['even'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.EVEN)])
    decks['stoneOnly'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.STONE)])
    decks['ironOnly'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.IRON)])
    decks['crystalOnly'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.CRYSTAL)])
    decks['stoneIron'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.STONE_IRON)])
    decks['stoneCrystal'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.STONE_CRYSTAL)])
    decks['ironCrystal'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.IRON_CRYSTAL)])
    # decks['stoneMostly'] = stoneAgePool + stoneAgePool[-3:0] + ironAgePool[0:2]
    # decks['stoneThresholdIronMostly'] = stoneAgePool[0:4] + ironAgePool + ironAgePool[-1:0]
    decks['4stoneEven'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.STONE),
        ai.fill_strat(4),
        ai.breakdown_strat(ai.Breakdown.IRON_CRYSTAL)
    ])
    # decks['strong'] = stoneAgePool[0:5] + ironAgePool[0:5] + crystalAgePool[0:10]
    decks['maxHard'] = ai.build_deck(pool, [ai.max_hard_synergy_strat()])
    decks['maxHardStone'] = ai.build_deck(pool, [ai.breakdown_strat(ai.Breakdown.STONE), ai.max_hard_synergy_strat()])
    for race in Race:
        decks[f'{race.name.lower()}HardSynergy'] = ai.hard_synergy(pool, race)
    for prof in Profession:
        decks[f'{prof.name.lower()}HardSynergy'] = ai.hard_synergy(pool, prof)

    decks['strongStoneIron'] = ai.build_deck(pool, [ai.strong_strat(), ai.breakdown_strat(ai.Breakdown.STONE_IRON)])
    decks['15StoneIron'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.STONE),
        ai.fill_strat(15),
        ai.breakdown_strat(ai.Breakdown.IRON)
    ])
    decks['18StoneIron'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.STONE),
        ai.fill_strat(18),
        ai.breakdown_strat(ai.Breakdown.IRON)
    ])

    decks['12StoneEven'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.STONE),
        ai.fill_strat(12),
        ai.breakdown_strat(ai.Breakdown.IRON_CRYSTAL)
    ])
    decks['15StoneEven'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.STONE),
        ai.fill_strat(15),
        ai.breakdown_strat(ai.Breakdown.IRON_CRYSTAL)
    ])
    decks['18StoneEven'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.STONE),
        ai.fill_strat(18),
        ai.breakdown_strat(ai.Breakdown.IRON_CRYSTAL)
    ])

    decks['17StoneCrystal'] = ai.build_deck(pool, [
        ai.breakdown_strat(ai.Breakdown.STONE),
        ai.fill_strat(18),
        ai.breakdown_strat(ai.Breakdown.CRYSTAL)
    ])

    for i in range(3):
        decks[f'rand{i}'] = ai.random_good_strategy(pool)

    for name1, deck1 in decks.items():
        wins[name1] = wins.get(name1, 0)
        if verbose:
            print('{0}{1}'.format(name1, deck_summary(deck1)))
        for name2, deck2 in decks.items():
            m = match(deck1, deck2)
            if m > 0:
                wins[name1] = wins[name1] + 1
            if name1 == 'YOU':
                print(f'{name1} vs {name2}: {m}')
        # wins.append((name1, wins / (len(decks) - 1) * 100))
    gamesPlayed += len(decks) - 1
    return (wins, gamesPlayed)


wins = {}
gamesPlayed = 0
sims = 10
try:
    sims = int(sys.argv[1])
    print(f'simulating {sims} times')
except (IndexError, ValueError):
    print('simulating 10 times')
for i in range(sims):
    (wins, gamesPlayed) = simulate(wins, gamesPlayed, verbose=sims == 1)


winPct = []
for deckName, wins in wins.items():
    winPct.append((deckName, wins / gamesPlayed * 100))
winPct = sorted(winPct, key=lambda t: t[1], reverse=True)
print()
for name, pct in winPct:
    print('{0} win%: {1:.0f}'.format(name, pct))
