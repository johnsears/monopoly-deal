import pytest

from monopoly_deal.cards import deck, Color
from monopoly_deal.game import Board

def test_find_cash_to_pay_bill_up_to_amount():
    board = Board(cash_cards=(deck[99], deck[100]), property_sets=tuple())  # $3 and $2

    cash_cards = board.find_cash_to_pay_bill_up_to_amount(bill_amount=3)
    assert len(cash_cards) == 1

    cash_cards = board.find_cash_to_pay_bill_up_to_amount(bill_amount=4)
    assert len(cash_cards) == 1
    assert Board.get_value_of_cards(cash_cards) == 3  # Expect to only fill up to 3

    cash_cards = board.find_cash_to_pay_bill_up_to_amount(bill_amount=5)
    assert len(cash_cards) == 2


def test_find_additional_cards_to_pay_bill():
    board = Board(cash_cards=(deck[99], deck[100]), property_sets=tuple())  # $3 and $2, utility and RR
    board = board.play_property_card(card=deck[37], color=Color.UTIL)
    board = board.play_property_card(card=deck[39], color=Color.RR)
    cash_cards = board.find_cash_to_pay_bill_up_to_amount(bill_amount=4)
    assert len(cash_cards) == 1
    assert Board.get_value_of_cards(cash_cards) == 3  # Expect to only fill up to 3

    payment_options = board.find_additional_cards_to_pay_bill(bill_amount=4, cards_in_payment=tuple(cash_cards))
    assert len(payment_options) == 3

    for cards_to_pay in payment_options:
        assert Board.get_value_of_cards(cards_to_pay) >= 4
        assert len(cards_to_pay) == 2

    payment_options = board.find_additional_cards_to_pay_bill(bill_amount=6, cards_in_payment=tuple(cash_cards))
    for cards_to_pay in payment_options:
        assert Board.get_value_of_cards(cards_to_pay) >= 6
        assert len(cards_to_pay) == 3


