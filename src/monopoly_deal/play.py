import random

from monopoly_deal.cards import *
from monopoly_deal.actions import *
from monopoly_deal.game import *

NUM_CARDS_TO_DRAW_IN_HAND = 5


def new_game(num_players: int):
    game_deck = list(deck.keys())
    random.shuffle(game_deck)

    players = []
    for index in range(num_players):
        hand = Hand(cards_in_hand=tuple(deck[game_deck.pop()] for _ in range(NUM_CARDS_TO_DRAW_IN_HAND)))
        players.append(
            Player(index=index, hand=hand, board=Board((), ()))
        )

    return Game(players=tuple(players), discard_pile=DiscardPile(discarded_cards=tuple()), current_turn_index=0, cards_played=0)

# def execute_action(game: Game, action: Action):



game = new_game(2)
