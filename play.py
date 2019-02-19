from card import generate_pool
import shutil
from textwrap import wrap

pool = generate_pool()
box = {
    'h': '─', 'v': '│',
    'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
    'lb': '├', 'rb': '┤', 'tb': '┬', 'bb': '┴',
    'cross': '┼'
}
cardInnerWidth = 18
cardInnerHeight = 8


def in_card(thing, fill=' '):
    thing = getattr(thing, 'name', thing)
    return str(thing)[:cardInnerWidth].lower().capitalize().ljust(cardInnerWidth, fill)


def add_detail_to_card(cardDispArr, detail):
    if len(cardDispArr) == 0:
        cardDispArr.append(in_card(detail, box['h']) + box['tb'])
    elif len(cardDispArr) < cardInnerHeight + 1:
        cardDispArr.append(in_card(detail) + box['v'])


def add_multiline_detail_to_card(cardDispArr, detail):
    detailArr = wrap(detail, cardInnerWidth)
    for subdetail in detailArr:
        add_detail_to_card(cardDispArr, subdetail)


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
        cardDispArr.extend([' ' * cardInnerWidth + box['v']] * (cardInnerHeight + 1 - len(cardDispArr)))
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
        add_detail_to_card(cardDispArr, str(card.strength) + 'str')
        add_detail_to_card(cardDispArr, card.age)
        add_detail_to_card(cardDispArr, card.prof)
        add_detail_to_card(cardDispArr, card.race)
        add_detail_to_card(cardDispArr, '')
        add_multiline_detail_to_card(cardDispArr, card.desc)
        finish_card(cardRows, cardDispArr)
        cardDispArr = []
    if len(cardRows[-1][0]) == 1:
        cardRows = cardRows[:-1]
    if len(cardRows) > 0:
        finish_card_row(cardRows[-1])
    for cardRow in cardRows:
        for cardStr in cardRow:
            print(cardStr)


def display_cards_old(cards):
    columns = shutil.get_terminal_size()[0]
    idLine = box['tl']
    strLine = box['v']
    ageLine = box['v']
    profLine = box['v']
    raceLine = box['v']
    blankLine = box['v']
    descLine = box['v']
    descLine2 = box['v']
    bottom = box['bl']
    justCapped = False

    for i, card in enumerate(cards):
        justCapped = False
        idLine = idLine + in_card(i, box['h']) + box['tb']
        strLine = strLine + in_card(str(card.strength) + 'str') + box['v']
        ageLine = ageLine + in_card(card.age) + box['v']
        profLine = profLine + in_card(card.prof) + box['v']
        raceLine = raceLine + in_card(card.race) + box['v']
        blankLine = blankLine + (' ' * cardInnerWidth) + box['v']
        descList = wrap(card.desc, cardInnerWidth)
        descList.append('')
        descList.append('')
        descLine = descLine + in_card(descList[0]) + box['v']
        descLine2 = descLine2 + in_card(descList[1]) + box['v']
        bottom = bottom + box['h'] * cardInnerWidth + box['bb']
        # if the next card will wrap around in columns
        if len(idLine) + cardInnerWidth + 1 > columns:
            justCapped = True
            print(idLine[:-1] + box['tr'])
            print(strLine[:-1] + box['v'])
            print(ageLine[:-1] + box['v'])
            print(profLine[:-1] + box['v'])
            print(raceLine[:-1] + box['v'])
            print(blankLine[:-1] + box['v'])
            print(descLine[:-1] + box['v'])
            print(descLine2[:-1] + box['v'])
            print(bottom[:-1] + box['br'])
            idLine = box['tl']
            strLine = box['v']
            ageLine = box['v']
            profLine = box['v']
            raceLine = box['v']
            blankLine = box['v']
            descLine = box['v']
            descLine2 = box['v']
            bottom = box['bl']

    if not justCapped:
        print(idLine[:-1] + box['tr'])
        print(strLine[:-1] + box['v'])
        print(ageLine[:-1] + box['v'])
        print(profLine[:-1] + box['v'])
        print(raceLine[:-1] + box['v'])
        print(blankLine[:-1] + box['v'])
        print(descLine[:-1] + box['v'])
        print(descLine2[:-1] + box['v'])
        print(bottom[:-1] + box['br'])


# deckMap = {}
# idea: input comma separated ints to enable or negative ints to disable cards in your deck
# while True:
#     deckChange = input('How?')


display_cards(pool)
display_cards([])
