import pytest

from monopoly_deal.cards import Color, deck
from monopoly_deal.game import PropertySet


def test_property_set_matches():
    pset = PropertySet(color=Color.BROWN, cards=(deck[43], ))

    assert pset.matches(colors=deck[44].colors)  # Another brown card
    assert pset.matches(colors=deck[65].colors)  # Full wild card
    assert pset.matches(colors=deck[73].colors)  # Brown wild card

    assert not pset.matches(colors=deck[54].colors)  # Red card
    assert not pset.matches(colors=deck[67].colors)  # Non Brown wild card

def test_add_card():
    pset = PropertySet(color=Color.BROWN, cards=(deck[43],))

    assert pset.add_card(card=deck[44]).is_complete()  # Add another brown card
    assert pset.add_card(card=deck[65]).is_complete()  # Add wild card works

    with pytest.raises(Exception):
        assert pset.add_card(card=deck[54])  # Can't add a red card
    with pytest.raises(Exception):
        assert pset.add_card(card=deck[67])  # Can't add a non-brown wild
    with pytest.raises(Exception):
        assert pset.add_card(card=deck[44]).add_card(65)  # Can't add three cards to a two-card set
    with pytest.raises(Exception):
        assert pset.add_card(card=deck[43])  # Can't add same card twice

def test_remove_card():
    pset = PropertySet(color=Color.BROWN, cards=(deck[43],))
    assert pset.remove_card(card=deck[43]).is_empty()

def test_add_house_and_hotel():
    pset = PropertySet(color=Color.BROWN, cards=(deck[43], ))
    assert not pset.can_add_house()
    assert not pset.can_add_hotel()

    pset = PropertySet(color=Color.BROWN, cards=(deck[43], deck[44]))
    assert pset.can_add_house()
    assert not pset.can_add_hotel()

    pset = PropertySet(color=Color.BROWN, cards=(deck[43], deck[44], deck[1]))  # Complete set with house
    assert pset.can_add_house()
    assert pset.can_add_hotel()

def test_get_rent_due():
    pset = PropertySet(color=Color.BROWN, cards=(deck[43],))

    assert pset.get_rent_due() == deck[43].rent[0]

    pset = PropertySet(color=Color.BROWN, cards=(deck[43], deck[44]))
    assert pset.get_rent_due() == deck[43].rent[1]

    pset = PropertySet(color=Color.BROWN, cards=(deck[43], deck[44], deck[1]))  # Complete set with house
    assert pset.get_rent_due() == (deck[43].rent[1] + 3)

    pset = PropertySet(color=Color.BROWN, cards=(deck[43], deck[44], deck[1], deck[2]))  # Complete set with 2 houses
    assert pset.get_rent_due() == (deck[43].rent[1] + 6)

    pset = PropertySet(color=Color.BROWN, cards=(deck[43], deck[44], deck[1], deck[4])) # Complete set with house and hotel
    assert pset.get_rent_due() == (deck[43].rent[1] + 3 + 4)