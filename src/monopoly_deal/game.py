import random

from itertools import combinations
from typing import Any, Union, Tuple, Set, List, Iterable

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
        assert self.matches(card.colors), "Card does not match the property's colors"
        assert card not in self.cards, "Cannot add a card twice"
        return PropertySet(color=self.color, cards=append_tuple(tup=self.cards, new_element=card))

    def remove_card(self, card: PropertyCard):
        assert card in self.cards, "Card is not in property set"
        new_cards = tuple([c for c in self.cards if c != card])
        return PropertySet(color=self.color, cards=new_cards)

    def matches(self, colors: Set[Color]):
        return Color.ALL in colors or self.color in colors

    def is_empty(self):
        return len(self.cards) == 0

    def get_built_properties(self):
        return [card for card in self.cards if card.buildable]

    def is_complete(self):
        non_house_or_hotel_cards = self.get_built_properties()
        return len(non_house_or_hotel_cards) >= len(property_set_rents[self.color])

    def can_add_house(self):
        return self.is_complete()

    def can_add_hotel(self):
        return len(self.houses) > 0

    def get_rent_due(self):
        non_house_or_hotel_cards = self.get_built_properties()

        if len(non_house_or_hotel_cards) == 0:
            return 0

        if self.is_complete():
            return property_set_rents[self.color][-1] + 3*len(self.houses) + 4*len(self.hotels)
        else:
            return property_set_rents[self.color][len(non_house_or_hotel_cards)-1]

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

    def play_property_card(self, card: PropertyCard, color: Color, is_bounty_from_charge: bool = False):
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
                    pset for pset in self.get_complete_sets() if pset.color == color
                ]
                if not is_bounty_from_charge:
                    existing_property_sets = [pset for pset in existing_property_sets if pset.can_add_house()]
                    assert len(existing_property_sets) > 0, "No complete sets to add to"
            elif card.name == HOTEL:
                existing_property_sets = [
                    pset for pset in self.get_complete_sets() if pset.color == color
                ]
                if not is_bounty_from_charge:
                    existing_property_sets = [pset for pset in existing_property_sets if pset.can_add_hotel()]
                    assert len(existing_property_sets) > 0, "No hotel eligible complete sets to add to"
            else:
                raise ValueError("Must play a property, house or hotel")

            if len(existing_property_sets) == 0 and is_bounty_from_charge:
                pset = PropertySet(color=color, cards=(card,))
                property_sets = append_tuple(tup=self.property_sets, new_element=pset)
            else:
                old_pset = existing_property_sets[0]
                pset = old_pset.add_card(card=card)
                property_sets = upsert_tuple(self.property_sets, new_element=pset, old_element=old_pset)
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
            pset for pset in self.property_sets if pset.matches(colors=card.colors) and not pset.is_complete()
        ]

    def get_property_set_containing_card(self, card: PropertyCard):
        for pset in self.get_property_sets_matching_colors(colors=card.colors):
            if card in pset.cards:
                return pset
        raise ValueError("No property sets contain this card.")

    def get_complete_sets(self):
        return [pset for pset in self.property_sets if pset.is_complete()]

    def get_property_sets_matching_colors(self, colors: Set[Color]):
        return [pset for pset in self.property_sets if pset.matches(colors)]

    def get_all_property_cards(self):
        return tuple([card for pset in self.property_sets for card in pset.cards])

    def get_total_value(self):
        return sum(card.value for card in self.get_all_property_cards() + self.cash_cards)

    def find_cash_to_pay_bill_up_to_amount(self, bill_amount: int):
        sorted_cash = sorted(self.cash_cards, key=lambda x: x.value, reverse=True)
        pay_with = []
        tally = 0
        for cash_card in sorted_cash:
            if cash_card.value <= (bill_amount-tally):
                tally += cash_card.value
                pay_with.append(cash_card)
            if tally >= bill_amount:
                break
        return tuple(pay_with)

    def find_additional_cards_to_pay_bill(self, bill_amount: int, cards_in_payment: Tuple[Card]):
        """Return all sets of cards that can pay for bill"""
        tally = Board.get_value_of_cards(cards=cards_in_payment)
        eligible_cards = [
            card for card in self.cash_cards + self.get_all_property_cards()
            if card not in cards_in_payment and card.value > 0
        ]
        potential_payments = self._powerset_with_minimum_value(iterable=eligible_cards, minimum_value_of_set=bill_amount - tally)
        return {frozenset(tuple(cards) + cards_in_payment) for cards in potential_payments}

    def serialize(self):
        return tuple(card.index for card in self.cash_cards), tuple(pset.serialize() for pset in self.property_sets)

    def _powerset_with_minimum_value(self, iterable, minimum_value_of_set: int):
        s = list(iterable)
        out = set()

        def unique(combo, out):
            """Filter out sets of cards that are supersets of existing payment options"""
            # This lets us find only minimally covering payments (you should never add cards to a payment that already
            # satisfies the charge)
            for el in out:
                if set(el).issubset(combo):
                    return False
            return True

        for r in range(1, len(s) + 1):
            out = out.union(
                {combo for combo in combinations(s, r) if unique(combo, out)
                    and self.get_value_of_cards(combo) >= minimum_value_of_set
                 }
            )
        return out

    def __repr__(self):
        return f'<Board: Cash: {self.cash_cards}, Properties: {self.property_sets}>'

    @staticmethod
    def get_value_of_cards(cards: Iterable[Card]):
        return sum([card.value for card in cards])


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

    def receive_cash_card(self, card: Cashable):
        return Player(
            index=self.index,
            hand=self.hand,
            board=self.board.play_card_as_cash(card=card)
        )

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
            board=self.board.play_property_card(card=card, color=color, is_bounty_from_charge=False)
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

    def add_property_card(self, card: PropertyCard, color: Color):
        return Player(
            index=self.index,
            hand=self.hand,
            board=self.board.play_property_card(card=card, color=color, is_bounty_from_charge=True)
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

    def discard_card(self, card: Card):
        assert card in self.hand.cards_in_hand, "Can't discard card that player does not have in hand"
        return Player(
            index=self.index,
            hand=self.hand.play_card(card=card),
            board=self.board
        )

    def serialize(self):
        return (self.hand.serialize(), self.board.serialize())

    def __repr__(self):
        return f'<Player {self.index}, Hand: {self.hand}, Board: {self.board}'


class Game:
    def __init__(self, players: Tuple[Player], discard_pile: DiscardPile, current_turn_index: int,
                 cards_played: int, game_deck: Tuple[Card]):
        self.players = players
        self.discard_pile = discard_pile
        self.current_turn_index = current_turn_index
        self.cards_played = cards_played
        self.game_deck = game_deck

    def current_player(self):
        return self.players[self.current_turn_index]

    def winner(self):
        for player in self.players:
            if len(player.board.get_complete_sets()) >= 3:
                return player

    def draw_cards(self, num_to_draw: int, player: Player = None, as_move: bool = False):
        discard_pile = self.discard_pile
        cards = tuple()
        game_deck = self.game_deck
        if num_to_draw >= len(game_deck):
            cards = tuple(deck[i] for i in game_deck)
            game_deck = [card.index for card in self.discard_pile.discarded_cards]
            random.shuffle(game_deck)
            game_deck = tuple(game_deck)
            discard_pile = DiscardPile(discarded_cards=tuple())
            num_to_draw -= len(cards)

        cards = cards + tuple(deck[game_deck[i]] for i in range(min(len(game_deck), num_to_draw)))
        game_deck = game_deck[num_to_draw:]

        player = player or self.current_player()
        new_player = player.draw_cards(cards=cards)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played + (1 if as_move else 0),
            game_deck=game_deck
        )

    def discard_card(self, card: Card, player: Player = None):
        player = player or self.current_player()
        new_player = player.discard_card(card=card)
        discard_pile = self.discard_pile.discard_card(card=card)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played,
            game_deck=self.game_deck
        )

    def play_cash_card(self, card: Union[ActionCard, CashCard]):
        player = self.current_player()
        new_player = player.play_cash_card(card=card)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played + 1,
            game_deck=self.game_deck
        )

    def play_property_card(self, card: PropertyCard, color: Color):
        player = self.current_player()
        new_player = player.play_property_card(card=card, color=color)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played + 1,
            game_deck=self.game_deck
        )

    def play_action_card(self, card: ActionCard, player: Player = None, is_response: bool = False):
        player = player or self.current_player()
        player = self.players[player.index]
        new_player = player.play_action_card(card=card)
        return Game(
            players=upsert_tuple(tup=self.players, new_element=new_player, old_element=player),
            discard_pile=self.discard_pile.discard_card(card=card),
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played + 1 if not is_response else 0,
            game_deck=self.game_deck
        )

    def steal_property_card(self, card: PropertyCard, stolen_to_player: Player, stolen_from_player: Player):
        stolen_to_player = self.players[stolen_to_player.index]
        stolen_from_player = self.players[stolen_from_player.index]

        current_color = stolen_from_player.board.get_property_set_containing_card(card=card).color
        new_stolen_to_player = stolen_to_player.add_property_card(card=card, color=current_color)
        new_stolen_from_player = stolen_from_player.lose_property_card(card=card)
        players = upsert_tuple(tup=self.players, new_element=new_stolen_to_player, old_element=stolen_to_player)
        players = upsert_tuple(tup=players, new_element=new_stolen_from_player, old_element=stolen_from_player)
        return Game(
            players=players,
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played,
            game_deck=self.game_deck
        )

    def steal_complete_set(self, property_set: PropertySet, stolen_to_player: Player, stolen_from_player: Player):
        stolen_to_player = self.players[stolen_to_player.index]
        stolen_from_player = self.players[stolen_from_player.index]

        new_stolen_to_player = stolen_to_player.add_property_set(property_set=property_set)
        new_stolen_from_player = stolen_from_player.lose_property_set(property_set=property_set)
        players = upsert_tuple(tup=self.players, new_element=new_stolen_to_player, old_element=stolen_to_player)
        players = upsert_tuple(tup=players, new_element=new_stolen_from_player, old_element=stolen_from_player)
        return Game(
            players=players,
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played,
            game_deck=self.game_deck
        )

    def charge_player(self, cash_cards: Tuple[Cashable], property_cards: Tuple[PropertyCard],
                      to_player: Player, from_player: Player):
        to_player = self.players[to_player.index]
        to_player_new = self.players[to_player.index]
        from_player = self.players[from_player.index]
        from_player_new = from_player.pay_cash(cards=cash_cards)

        for card in property_cards:
            current_color = from_player_new.board.get_property_set_containing_card(card=card).color
            from_player_new = from_player_new.lose_property_card(card=card)
            to_player_new = to_player_new.add_property_card(card=card, color=current_color)
        for cash_card in cash_cards:
            to_player_new = to_player_new.receive_cash_card(card=cash_card)
        players = upsert_tuple(tup=self.players, new_element=from_player_new, old_element=from_player)
        players = upsert_tuple(tup=players, new_element=to_player_new, old_element=to_player)
        return Game(
            players=players,
            discard_pile=self.discard_pile,
            current_turn_index=self.current_turn_index,
            cards_played=self.cards_played,
            game_deck=self.game_deck
        )

    def end_turn(self):
        return Game(
            players=self.players,
            discard_pile=self.discard_pile,
            current_turn_index=self.get_next_player_index(),
            cards_played=0,
            game_deck=self.game_deck
        )

    def serialize(self):
        return (
            tuple(player.serialize() for player in self.players), self.discard_pile.serialize(), self.current_turn_index.index
        )

    def get_next_player_index(self):
        ind = (self.current_turn_index + 1) % len(self.players)
        return ind
