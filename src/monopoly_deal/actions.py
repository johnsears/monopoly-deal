from typing import List, Union

from monopoly_deal.cards import *
from monopoly_deal.game import *

class Action:
    respondable = False


class Charge(Action):
    def __init__(self, charge_player: Player, amount: int):
        self.charge_player = charge_player
        self.amount = amount
        self.respondable = True


class Steal(Action):
    def __init__(self, steal_from_player: Player, steal_card: PropertyCard):
        self.steal_from_player = steal_from_player
        self.steal_card = steal_card
        self.respondable = True


class Swap(Action):
    def __init__(self, steal_from_player: Player, steal_card: PropertyCard, give_card: PropertyCard):
        self.steal_from_player = steal_from_player
        self.steal_card = steal_card
        self.give_card = give_card
        self.respondable = True


class Pay(Action):
    def __init__(self, cash_cards: List[Card], property_cards: List[PropertyCard]):
        self.cash_cards = cash_cards
        self.property_cards = property_cards
        self.respondable = False

    def get_amount(self):
        return sum([card.value for card in self.cash_cards + self.property_cards])


class Discard(Action):
    def __init__(self, discard_card: Card):
        self.discard_card = discard_card
        self.respondable = False


class ChangeColor(Action):
    def __init__(self, property_card: PropertyCard, to_color: Color):
        self.property_card = property_card
        self.to_color = to_color
        self.respondable = False


class Draw(Action):
    def __init__(self):
        self.respondable = False


class SayNo(Action):
    def __init__(self):
        self.respondable = True


class DoubleCharge(Action):
    def __init__(self):
        self.respondable = True


class PlayProperty(Action):
    def __init__(self, property_card: PropertyCard, color: Color):
        self.property_card = property_card
        self.color = color
        self.respondable = False


class PlayAsCash(Action):
    def __init__(self, cash_card: Union[CashCard, ActionCard]):
        self.cash_card = cash_card
        self.respondable = False
