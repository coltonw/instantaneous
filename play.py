import shutil
from textwrap import wrap
from card import generate_pool
from match import DECK_SIZE, match, deck_summary
import ai

pool = generate_pool()
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
        add_detail_to_card(cardDispArr, i)
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


# deckMap = {}
# idea: input comma separated ints to enable or negative ints to disable cards in your deck
# while True:
#     deckChange = input('How?')


display_cards(pool)


# print(f'Pool:\n{pool}\n')
# stoneAgePool = list(filter(lambda card: card.age == Age.STONE, pool))
# ironAgePool = list(filter(lambda card: card.age == Age.IRON, pool))
# crystalAgePool = list(filter(lambda card: card.age == Age.CRYSTAL, pool))
# strongPool = list(filter(lambda card: card.race == Race.BEASTMAN, pool))
# weakPool = list(filter(lambda card: card.race != Race.BEASTMAN, pool))

decks = {}
decks['even'] = ai.even(pool)
# decks['stoneOnly'] = stoneAgePool + stoneAgePool[-5:0]
# decks['ironOnly'] = ironAgePool + ironAgePool[-5:0]
# decks['crystalOnly'] = crystalAgePool + crystalAgePool[-5:0]
decks['stoneIron'] = ai.stone_iron(pool)
# decks['stoneCrystal'] = stoneAgePool[0:10] + crystalAgePool[0:10]
# decks['ironCrystal'] = ironAgePool[0:10] + crystalAgePool[0:10]
# decks['stoneMostly'] = stoneAgePool + stoneAgePool[-3:0] + ironAgePool[0:2]
# decks['stoneThresholdIronMostly'] = stoneAgePool[0:4] + ironAgePool + ironAgePool[-1:0]
decks['stoneThresholdEven'] = ai.low_stone(pool)
# decks['strong'] = stoneAgePool[0:5] + ironAgePool[0:5] + crystalAgePool[0:10]
for i in range(DECK_SIZE - len(decks)):
    # multi sample makes it more possible that we repeat cards more which causes more variety in deck breakdown.
    decks[f'rand{i}'] = ai.strong(pool)

winPct = []
for name1, deck1 in decks.items():
    print('{0}{1}'.format(name1, deck_summary(deck1)))
    wins = 0
    for name2, deck2 in decks.items():
        m = match(deck1, deck2)
        if m > 0:
            wins += 1
        # print(f'{name1} vs {name2}: {m}')
    winPct.append((name1, wins / len(decks) * 100))
print()

winPct = sorted(winPct, key=lambda t: t[1], reverse=True)
for name, pct in winPct:
    print('{0} win%: {1:.0f}'.format(name, pct))
