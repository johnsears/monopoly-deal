import logging
from typing import Dict

from monopoly_deal.cards import *
from monopoly_deal.agents import RandomAgent, Agent
from monopoly_deal.actions import *
from monopoly_deal.game import *

NUM_CARDS_TO_DRAW_IN_HAND = 5

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def is_rejected(actions: List[Tuple[Player, Card, Action]]):
    reject = -1
    ind = 1
    while True:
        player, cards_to_play, action = actions[-ind]
        if isinstance(action, SayNo):
            reject *= -1
            ind += 1
        else:
            break
    return reject == 1


def execute_actions(game: Game, actions: List[Tuple[Player, Card, Action]]):
    # Check if whole thing is moot
    if is_rejected(actions=actions):
        for player, card, action in actions:
            logger.info(f'{player.index}: played {card} but was rejected')
            is_response = player != game.current_player()
            game = game.play_action_card(card=card, player=player, is_response=is_response)
    else:
        # Otherwise play them out
        for player, card, action in actions:
            # print(f'{player.index} ({game.cards_played}): played {card} to drive {action}')
            if isinstance(action, Pay):
                game = game.charge_player(
                    cash_cards=action.cash_cards,
                    property_cards=action.property_cards,
                    to_player=action.target_player,
                    from_player=player
                )
            elif isinstance(action, NoResponse):
                pass  # Don't do anything
            else:
                if isinstance(action, Charge):
                    game = game.play_action_card(card=card, player=player)
                elif isinstance(action, StealCard):
                    game = game.play_action_card(card=card, player=player)
                    game = game.steal_property_card(
                        card=action.steal_card,
                        stolen_to_player=player,
                        stolen_from_player=action.target_player
                    )
                elif isinstance(action, StealSet):
                    game = game.play_action_card(card=card, player=player)
                    game = game.steal_complete_set(
                        property_set=action.steal_set,
                        stolen_to_player=player,
                        stolen_from_player=action.target_player
                    )
                elif isinstance(action, Swap):
                    game = game.play_action_card(card=card, player=player)
                    game = game.steal_property_card(
                        card=action.steal_card,
                        stolen_to_player=player,
                        stolen_from_player=action.target_player
                    )
                    game = game.steal_property_card(
                        card=action.give_card,
                        stolen_to_player=action.target_player,
                        stolen_from_player=player
                    )
                elif isinstance(action, ChangeColor):
                    pass
                elif isinstance(action, Draw):
                    game = game.draw_cards(num_to_draw=action.num_to_draw, as_move=True)
                elif isinstance(action, SayNo):
                    is_response = player != game.current_player()
                    game = game.play_action_card(card=card, player=player, is_response=is_response)
                elif isinstance(action, PlayProperty):
                    game = game.play_property_card(card=action.property_card, color=action.color)
                elif isinstance(action, PlayAsCash):
                    game = game.play_cash_card(card=action.cash_card)
                elif isinstance(action, Discard):
                    for card in action.discard_cards:
                        game = game.discard_card(card=card)

    return game


def new_game(num_players: int):
    game_deck = list(deck.keys())
    random.shuffle(game_deck)

    players = []
    for index in range(num_players):
        hand = Hand(cards_in_hand=tuple())
        players.append(Player(index=index, hand=hand, board=Board((), ())))
    game = Game(
        players=tuple(players),
        discard_pile=DiscardPile(discarded_cards=tuple()),
        current_turn_index=0,
        cards_played=0,
        game_deck=tuple(game_deck)
    )
    for player in players:
        game = game.draw_cards(num_to_draw=NUM_CARDS_TO_DRAW_IN_HAND, player=player)
    return game


def get_available_actions_for_player(player: Player, game: Game):
    card_actions = {}
    for card in player.hand.cards_in_hand:
        available_actions = get_available_actions(card=card, players=game.players, current_player=player)
        if available_actions:
            card_actions[card] = available_actions
    card_actions[None] = [EndTurn()]
    return card_actions


def play_game(game: Game, agents: Dict[Player, Agent]):
    n_turns = 0
    while not game.winner():
        current_player = game.current_player()
        game = game.draw_cards(num_to_draw=2)
        while game.cards_played < MAX_PLAYS_PER_TURN and current_player.index == game.current_player().index:
            current_player = game.current_player()
            available_actions = get_available_actions_for_player(player=current_player, game=game)
            # Maintain a list of valid plays
            # Each element is a tuple of
            # 1. Player
            # 2. Set of cards to play (will only be one unless it's a payment)
            # 3. Action to be executed
            actions = []
            card_to_play, action = agents[current_player.index].get_action(game, [], available_actions)
            if isinstance(action, EndTurn):
                break

            actions.append((current_player, card_to_play, action))
            while action.respondable:
                player = action.target_player
                prev_action = action

                available_responses = get_available_responses(player=player, actions=actions)
                card_to_play, action = agents[player.index].get_response(game, actions, available_responses)

                if isinstance(prev_action, Charge):
                    assert isinstance(action, Pay) or isinstance(action, SayNo), "Must either pay or reject a charge"
                    if isinstance(action, Pay):
                        assert (action.get_amount() >= prev_action.amount or
                                action.get_amount() == player.board.get_total_value()), "Must pay in full"

                actions.append((player, card_to_play, action))
            game = execute_actions(game, actions)

        # Force a discard if player has too many cards left
        current_player = game.current_player()
        if len(current_player.hand.cards_in_hand) > MAX_CARDS_IN_HAND:
            discard_options = get_discard_options(player=current_player)
            action = agents[current_player.index].get_discard_action(game, actions, discard_options)
            actions = [(current_player, None, action)]
            game = execute_actions(game, actions)

        game = game.end_turn()
        n_turns += 1
        if len(game.game_deck) == 0:
            print("Out of cards")
            break
    return game


def sim_new_game():
    game = new_game(2)
    agents = {player.index: RandomAgent() for player in game.players}
    game = play_game(game=game, agents=agents)
    return game

