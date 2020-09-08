from typing import List, Union

from monopoly_deal.cards import *
from monopoly_deal.game import *

class Action:
    respondable = False


class EndTurn(Action):
    pass


class NoResponse(Action):
    pass

class Charge(Action):
    def __init__(self, charge_player: Player, amount: int):
        self.target_player = charge_player
        self.amount = amount
        self.respondable = True

    def __repr__(self):
        return f'<Charge ${self.amount} to player {self.target_player.index}>'


class StealCard(Action):
    def __init__(self, steal_from_player: Player, steal_card: PropertyCard):
        self.target_player = steal_from_player
        self.steal_card = steal_card
        self.respondable = True

    def __repr__(self):
        return f'<StealCard {self.steal_card}>>'


class StealSet(Action):
    def __init__(self, steal_from_player: Player, steal_set: PropertySet):
        self.target_player = steal_from_player
        self.steal_set = steal_set
        self.respondable = True

    def __repr__(self):
        return f'<StealSet {self.steal_set.color} from player {self.target_player.index}>'

class Swap(Action):
    def __init__(self, steal_from_player: Player, steal_card: PropertyCard, give_card: PropertyCard):
        self.target_player = steal_from_player
        self.steal_card = steal_card
        self.give_card = give_card
        self.respondable = True

    def __repr__(self):
        return f'<Swap {self.steal_card} for {self.give_card}>'

class Pay(Action):
    def __init__(self, pay_to_player: Player, cash_cards: Tuple[Card], property_cards: Tuple[PropertyCard]):
        self.target_player = pay_to_player
        self.cash_cards = cash_cards
        self.property_cards = property_cards
        self.respondable = False

    def get_amount(self):
        return Board.get_value_of_cards(cards=self.cash_cards + self.property_cards)

    def __repr__(self):
        return f'<Pay {self.cash_cards} + {self.property_cards} to {self.target_player.index}'

class Discard(Action):
    def __init__(self, discard_card: Card):
        self.discard_card = discard_card
        self.respondable = False


class ChangeColor(Action):
    def __init__(self, property_card: PropertyCard, to_color: Color):
        self.property_card = property_card
        self.to_color = to_color
        self.respondable = False

    def __repr__(self):
        return f'<ChangeColor {self.property_card} to {self.to_color}>'

class Draw(Action):
    def __init__(self, num_to_draw: int):
        self.respondable = False
        self.num_to_draw = num_to_draw


class SayNo(Action):
    def __init__(self, to_player: Player):
        self.respondable = True
        self.target_player = to_player


class DoubleCharge(Action):
    def __init__(self):
        self.respondable = True


class PlayProperty(Action):
    def __init__(self, property_card: PropertyCard, color: Color):
        self.property_card = property_card
        self.color = color
        self.respondable = False

    def __repr__(self):
        return f'<PlayProperty {self.property_card.name}> as {self.color}>'


class PlayAsCash(Action):
    def __init__(self, cash_card: Cashable):
        self.cash_card = cash_card
        self.respondable = False

    def __repr__(self):
        return f'<PlayAsCash {self.cash_card}>'


def get_available_actions(card: Card, players: Tuple[Player], current_player: Player):
    available_actions = []
    if isinstance(card, CashCard):
        available_actions = [PlayAsCash(cash_card=card)]
    elif isinstance(card, PropertyCard):
        if card.buildable:
            if Color.ALL not in card.colors:
                for color in card.colors:
                    available_actions.append(PlayProperty(property_card=card, color=color))
            else:
                for color in Color:
                    if color != Color.ALL:
                        available_actions.append(PlayProperty(property_card=card, color=color))
        else:
            for property_set in current_player.board.get_complete_sets():
                if property_set.can_add_house() and card.name == HOUSE:
                    available_actions.append(PlayProperty(property_card=card, color=property_set.color))
                elif property_set.can_add_hotel() and card.name == HOTEL:
                    available_actions.append(PlayProperty(property_card=card, color=property_set.color))
    elif isinstance(card, RentCard):
        available_actions = [PlayAsCash(cash_card=card)]
        matching_property_sets = current_player.board.get_property_sets_matching_colors(colors=card.colors)
        if len(matching_property_sets) > 0:
            best_rent = max([pset.get_rent_due() for pset in matching_property_sets])
            for opposing_player in players:
                if opposing_player != current_player:
                    available_actions.append(Charge(charge_player=opposing_player, amount=best_rent))
    elif isinstance(card, ActionCard):
        available_actions = [PlayAsCash(cash_card=card)]
        if card.action_type == ActionType.PASS_GO:
            available_actions.append(Draw(2))
        else:
            for opposing_player in players:
                if opposing_player != current_player:
                    if card.action_type == ActionType.BDAY:
                        available_actions.append(Charge(charge_player=opposing_player, amount=2))
                    elif card.action_type == ActionType.DEAL_BREAKER:
                        for complete_set in opposing_player.board.get_complete_sets():
                            available_actions.append(StealSet(steal_from_player=opposing_player, steal_set=complete_set))
                    elif card.action_type == ActionType.DEBT_COLLECTOR:
                        available_actions.append(Charge(charge_player=opposing_player, amount=5))
                    elif card.action_type in (ActionType.SLY_DEAL, ActionType.FORCED_DEAL):
                        for property_set in opposing_player.board.property_sets:
                            if not property_set.is_complete():
                                for property_card in property_set.cards:
                                    if card.action_type == ActionType.SLY_DEAL:
                                        available_actions.append(
                                            StealCard(steal_from_player=opposing_player, steal_card=property_card)
                                        )
                                    else:
                                        for own_property_set in current_player.board.property_sets:
                                            if not own_property_set.is_complete():
                                                for own_property_card in own_property_set.cards:
                                                    available_actions.append(
                                                        Swap(
                                                            steal_from_player=opposing_player,
                                                            steal_card=property_card,
                                                            give_card=own_property_card
                                                        )
                                                    )
    return available_actions

