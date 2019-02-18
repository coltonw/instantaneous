from card import generate_pool
import shutil

pool = generate_pool()
box = {
    'h': '─', 'v': '│',
    'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
    'lb': '├', 'rb': '┤', 'tb': '┬', 'bb': '┴',
    'cross': '┼'
}
cardInnerWidth = 7


def in_card(thing, fill=' '):
    thing = getattr(thing, 'name', thing)
    return str(thing)[:cardInnerWidth].lower().capitalize().ljust(cardInnerWidth, fill)


def display_cards(cards):
    columns = shutil.get_terminal_size((80, 20))[0]
    idLine = box['tl']
    strLine = box['v']
    ageLine = box['v']
    profLine = box['v']
    raceLine = box['v']
    descLine = box['v']
    bottom = box['bl']
    justCapped = False

    for i, card in enumerate(cards):
        justCapped = False
        idLine = idLine + in_card(i, box['h']) + box['tb']
        strLine = strLine + in_card(str(card.strength) + 'str') + box['v']
        ageLine = ageLine + in_card(card.age) + box['v']
        profLine = profLine + in_card(card.prof) + box['v']
        raceLine = raceLine + in_card(card.race) + box['v']
        descLine = descLine + in_card(card.desc or '') + box['v']
        bottom = bottom + box['h'] * cardInnerWidth + box['bb']
        # if the next card will wrap around in columns
        if len(idLine) + cardInnerWidth + 1 > columns:
            justCapped = True
            print(idLine[:-1] + box['tr'])
            print(strLine[:-1] + box['v'])
            print(ageLine[:-1] + box['v'])
            print(profLine[:-1] + box['v'])
            print(raceLine[:-1] + box['v'])
            print(descLine[:-1] + box['v'])
            print(bottom[:-1] + box['br'])
            idLine = box['tl']
            strLine = box['v']
            ageLine = box['v']
            profLine = box['v']
            raceLine = box['v']
            descLine = box['v']
            bottom = box['bl']

    if not justCapped:
        print(idLine[:-1] + box['tr'])
        print(strLine[:-1] + box['v'])
        print(ageLine[:-1] + box['v'])
        print(profLine[:-1] + box['v'])
        print(raceLine[:-1] + box['v'])
        print(descLine[:-1] + box['v'])
        print(bottom[:-1] + box['br'])


# deckMap = {}
# idea: input comma separated ints to enable or negative ints to disable cards in your deck
# while True:
#     deckChange = input('How?')


display_cards(pool)
