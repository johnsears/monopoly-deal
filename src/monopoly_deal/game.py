from typing import Any, Union, Tuple

from monopoly_deal.cards import *

MAX_PLAYS_PER_TURN = 3

def append_tuple(tup: Tuple, new_element: Any) -> Tuple:
    return tup + (new_element,)


def remove_from_tuple(tup: Tuple, delete_element: Any) -> Tuple:
    ind = tup.index(delete_element)
    return tup[:ind] + tup[(ind + 1):]


def upsert_tuple(tup: Tuple, new_element: Any, old_element: Any = None):
    if old_element is not None:
        ind = tup.index(old_element)
    else:
        ind = len(tup)
    return tup[:ind] + (new_element, ) + tup[(ind+1):]


class PropertySet:
    def __init__(self, color: Color, cards: Tuple[PropertyCard]):
        assert color != color.ALL, "Cannot create a wildcard color property set"

        self.color = color
        self.cards = cards

        self.houses = [card for card in cards if card.name == HOUSE]
        self.hotels = [card for card in cards if card.name == HOTEL]

    def add_card(self, card: PropertyCard):
        assert self.matches(card), "Card does not match the property's colors"
        assert card not in self.cards, "Cannot add a card twice"
        return PropertySet(color=self.color, cards=append_tuple(tup=self.cards, new_element=card))

    def remove_card(self, card: PropertyCard):
        assert card in self.cards, "Card is not in property set"
        new_cards = tuple([c for c in self.cards if c != card])
        return PropertySet(color=self.color, cards=new_cards)

    def matches(self, card: PropertyCard):
        return Color.ALL in card.color or self.color in card.color

    def is_empty(self):
        return len(self.cards) == 0

    def is_complete(self):
        return len(self.cards) >= len(property_set_rents[self.color])

    def can_add_house(self):
        return self.is_complete()

    def can_add_hotel(self):
        return len(self.houses) > 0

    def get_rent_due(self):
        if len(self.cards) == 0:
            return 0

        if self.is_complete():
            return property_set_rents[self.color][-1] + 3*len(self.houses) + 4*len(self.hotels)
        else:
            return property_set_rents[self.color][len(self.cards)-1]

    def serialize(self):
        return tuple(card.index for card in self.cards)

    def __repr__(self):
        return f'<Property Set[{self.color}]: {len(self.cards)}>'


class CardLocation:
    pass


class Hand(CardLocation):
    def __init__(self, cards_in_hand: Tuple[Card, ...]):
        self.cards_in_hand = cards_in_hand

    def play_card(self, card: Card):
        return Hand(cards_in_hand=remove_from_tuple(tup=self.cards_in_hand, delete_element=card))

    def draw_cards(self, cards: Tuple[Card]):
        return Hand(cards_in_hand=self.cards_in_hand + cards)

    def serialize(self):
        return tuple(card.index for card in self.cards_in_hand)

    def __repr__(self):
        return f'<Hand {self.cards_in_hand}>'


class Board(CardLocation):
    def __init__(self, cash_cards: Tuple[Cashable], property_sets: Tuple[PropertySet]):
        self.cash_cards = cash_cards
        self.property_sets = property_sets

    def play_card_as_cash(self, card: Cashable):
        return Board(cash_cards=append_tuple(self.cash_cards, card), property_sets=self.property_sets)

    def play_property_card(self, card: PropertyCard, color: Color):
        if card.buildable:
            # Check if there is an existing property set to add this to
            existing_property_sets = [
                pset for pset in self.get_playable_property_sets_for_card(card)
                    if pset.color == color and not pset.is_complete()
            ]
            # If not, then create  one
            if len(existing_property_sets) == 0:
                pset = PropertySet(color=color, cards=(card,))
                property_sets = append_tuple(tup=self.property_sets, new_element=pset)
            else:
                old_pset = existing_property_sets[0]
                pset = old_pset.add_card(card=card)
                property_sets = upsert_tuple(tup=self.property_sets, new_element=pset, old_element=old_pset)
        else:
            if card.name == HOUSE:
                existing_property_sets = [
                    pset for pset in self.get_playable_property_sets_for_card(card)
                    if pset.color == color and pset.can_add_house()
                ]
                assert len(existing_property_sets) > 0, "No complete sets to add to"
            elif card.name == HOTEL:
                existing_property_sets = [
                    pset for pset in self.get_playable_property_sets_for_card(card)
                    if pset.color == color and pset.can_add_hotel()
                ]
                assert len(existing_property_sets) > 0, "No hotel eligible complete sets to add to"
            else:
                raise ValueError("Must play a property, house or hotel")

            old_pset = existing_property_sets[0]
            pset = old_pset.add_card(card=card)
            property_sets = self._update_property_set(new_set=pset, old_set=old_pset)
        return Board(cash_cards=self.cash_cards, property_sets=property_sets)

    def lose_property_card(self, card: PropertyCard):
        pset = self.get_property_set_containing_card(card=card)
        new_pset = pset.remove_card(card=card)
        return Board(
            cash_cards=self.cash_cards,
            property_sets=upsert_tuple(tup=self.property_sets, new_element=new_pset, old_element=pset)
        )

    def lose_property_set(self, property_set: PropertySet):
        return Board(
            cash_cards=self.cash_cards,
            property_sets=remove_from_tuple(tup=self.property_sets, delete_element=property_set)
        )

    def add_property_set(self, property_set: PropertySet):
        return Board(
            cash_cards=self.cash_cards,
            property_sets=append_tuple(tup=self.property_sets, new_element=property_set)
        )

    def pay_cash(self, cards: Tuple[Cashable]):
        new_cash_cards = tuple(card for card in self.cash_cards if card not in cards)
        return Board(cash_cards=new_cash_cards, property_sets=self.property_sets)

    def get_playable_property_sets_for_card(self, card: PropertyCard):
        return [
            pset for pset in self.property_sets if pset.matches(card=card) and not pset.is_complete()
        ]

    def get_property_set_containing_card(self, card: PropertyCard):
        for pset in self.get_playable_property_sets_for_card(card=card):
            if card in pset.cards:
                return pset
        raise ValueError("No property sets contain this card.")

    def serialize(self):
        return tuple(card.index for card in self.cash_cards), tuple(pset.serialize() for pset in self.property_sets)

    def __repr__(self):
        return f'<Board: Cash: {self.cash_cards}, Properties: {self.property_sets}>'


class DiscardPile(CardLocation):
    def __init__(self, discarded_cards: Tuple[Card]):
        self.discarded_cards = discarded_cards

    def discard_card(self, card: Card):
        return DiscardPile(discarded_cards=append_tuple(self.discarded_cards, card))

    def serialize(self):
        return tuple(card.index for card in self.discarded_cards)


class Player:
    def __init__(self, index: int, hand: Hand, board: Board):
        self.index = index
        self.hand = hand
        self.board = board

    def play_action_card(self, card: ActionCard):
        return Player(index=self.index, hand=self.hand.play_card(card=card), board=self.board)

    def play_cash_card(self, card: Cashable):
        return Player(
            index=self.index,
            hand=self.hand.play_card(card=card),
            board=self.board.play_card_as_cash(card=card)
        )

    def play_property_card(self, card: PropertyCard, color: Color):
        return Player(
            index=self.index,
            hand=self.hand.play_card(card=card),
            board=self.board.play_property_card(card=card, color=color)
        )

    def draw_cards(self, cards: Tuple[Card]):
        return Player(
            index=self.index,
            hand=self.hand.draw_cards(cards=cards),
            board=self.board
        )

    def pay_cash(self, cards: Tuple[Cashable]):
        return Player(
            index=self.index,
            hand=self.hand,
            board=self.board.pay_cash(cards=cards)
        )

    def lose_property_card(self, card: PropertyCard):
        return Player(
            index=self.index,
            hand=self.hand,
            board=self.board.lose_property_card(card=card)
        )

    def lose_property_set(self, property_set: PropertySet):
        return Player(
            index=self.index,
            hand=self.hand,
            board=self.board.lose_property_set(property_set=property_set)
        )

    def add_property_set(self, property_set: PropertySet):
        return Player(
            index=self.index,
            hand=self.hand,
            board=self.board.add_property_set(property_set=property_set)
        )

    def serialize(self):
        return (self.hand.serialize(), self.board.serialize())

    def __repr__(self):
        return f'<Player {self.index}, Hand: {self.hand}, Board: {self.board}'


class Game:
    def __init__(self, players: Tuple[Player], discard_pile: DiscardPile, current_turn_index: int, cards_played: int):
        self.players = players
        self.discard_pile = discard_pile
        self.current_turn_index = current_turn_index
        self.cards_played = cards_played

    def draw_cards(self, cards: Tuple[Card]):
        player = self.players[self.current_turn_index]
        new_player = player.draw_cards(cards=cards)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played
        )

    def play_cash_card(self, card: Union[ActionCard, CashCard]):
        player = self.players[self.current_turn_index]
        new_player = player.play_cash_card(card=card)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played + 1
        )

    def play_property_card(self, card: PropertyCard):
        player = self.players[self.current_turn_index]
        new_player = player.play_property_card(card=card)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played + 1
        )

    def play_action_card(self, card: ActionCard):
        player = self.players[self.current_turn_index]
        new_player = player.play_action_card(card=card)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=self.discard_pile.discard_card(card=card),
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played + 1
        )

    def steal_property_card(self, card: PropertyCard, stolen_to_player: Player, stolen_from_player: Player):
        current_color = stolen_from_player.board.get_property_set_containing_card(card=card).color
        new_stolen_to_player = stolen_to_player.play_property_card(card=card, color=current_color)
        new_stolen_from_player = stolen_from_player.lose_property_card(card=card)
        players = upsert_tuple(tup=self.players, new_element=new_stolen_to_player, old_element=stolen_to_player)
        players = upsert_tuple(tup=players, new_element=new_stolen_from_player, old_element=stolen_from_player)
        return Game(
            players=players,
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played
        )

    def steal_complete_set(self, property_set: PropertySet, stolen_to_player: Player, stolen_from_player: Player):
        new_stolen_to_player = stolen_to_player.add_property_set(property_set=property_set)
        new_stolen_from_player = stolen_from_player.lose_property_set(property_set=property_set)
        players = upsert_tuple(tup=self.players, new_element=new_stolen_to_player, old_element=stolen_to_player)
        players = upsert_tuple(tup=players, new_element=new_stolen_from_player, old_element=stolen_from_player)
        return Game(
            players=players,
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played
        )

    def charge_cash(self, cash_cards: Tuple[Cashable], to_player: Player, from_player: Player):
        from_player_new = from_player.pay_cash(cards=cash_cards)
        to_player_new = to_player
        for cash_card in cash_cards:
            to_player_new = to_player_new.play_cash_card(card=cash_card)
        players = upsert_tuple(tup=self.players, new_element=from_player_new, old_element=from_player)
        players = upsert_tuple(tup=players, new_element=to_player_new, old_element=to_player)
        return Game(
            players=players,
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played
        )

    def serialize(self):
        return (
            tuple(player.serialize() for player in self.players), self.discard_pile.serialize(), self.current_turn_index.index
        )

    def get_next_player(self):
        ind = (self.players.index(self.current_turn_index) + 1) % len(self.players)
        return self.players[ind]

