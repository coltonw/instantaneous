from instantaneous.game import card


def test_card_to_proto():
    c = card.Card([3, 3, 3], card.Age.STONE, card.Race.UNDEAD, card.Profession.ALCHEMIST)
    c.to_proto()
