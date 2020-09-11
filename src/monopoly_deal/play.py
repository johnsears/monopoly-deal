import logging
from typing import Dict

from monopoly_deal.cards import *
from monopoly_deal.agents import RandomAgent, Agent
from monopoly_deal.actions import *
from monopoly_deal.game import *

NUM_CARDS_TO_DRAW_IN_HAND = 5

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def execute_actions(game: Game, actions: List[Tuple[Player, Card, Action]], debug=False):
    # Check if whole thing is moot
    if is_rejected(actions=actions):
        for player, card, action in actions:
            logger.info(f'{player.index}: played {card} but was rejected')
            is_response = player != game.current_player()
            game = game.play_action_card(card=card, player=player, is_response=is_response)
    else:
        # Otherwise play them out
        for player, card, action in actions:
            logger.debug(f'{player.index} ({game.cards_played}): played {card} to drive {action}')
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
        game_deck=tuple(game_deck),
        state=0
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


def step(game: Game, card_to_play: Card, action: Action, actions: Tuple = None, debug=False):
    # Maintain a list of valid plays in `actions`
    # Each element is a tuple of
    # 1. Player
    # 2. Set of cards to play (will only be one unless it's a payment)
    # 3. Action to be executed
    while not game.winner():
        current_player = game.current_player()
        if game.state == 0:
            logger.debug(f"{current_player.index} Draw cards")
            game = game.draw_cards(num_to_draw=2)
            game = game.set_state(1)
        if 1 <= game.state < 3:
            while game.cards_played < MAX_PLAYS_PER_TURN and current_player.index == game.current_player().index:
                current_player = game.current_player()
                if game.state == 1:
                    logger.debug(f"{current_player.index} Get actions")
                    available_actions = get_available_actions_for_player(player=current_player, game=game)
                    return current_player, game.set_state(1.5), tuple(), available_actions, game.winner() is not None
                if game.state == 1.5:
                    logger.debug(f"{current_player.index} Take action {action}")
                    if isinstance(action, EndTurn):
                        logger.debug(f"{current_player.index} End turn")
                        break
                    actions = append_tuple(tup=actions, new_element=(current_player, card_to_play, action))
                    game = game.set_state(2)
                if 2 <= game.state < 3:
                    last_action = actions[-1][2]  # Get most recent action
                    while last_action.respondable:
                        player = last_action.target_player
                        if game.state == 2:
                            logger.debug(f"{player.index} Get response to {last_action}")
                            available_responses = get_available_responses(player=player, actions=actions)
                            return player, game.set_state(2.5), actions, available_responses, game.winner() is not None
                        if game.state == 2.5:
                            actions = append_tuple(tup=actions, new_element=(player, card_to_play, action))
                            logger.debug(f"{player.index} Respond with  {action}")
                            game = game.set_state(2)
                            last_action = action
                    game = execute_actions(game, actions, debug=debug)
                    actions = tuple()  # Reset actions
                    game = game.set_state(1)
                    logger.debug(f"{current_player.index} End of play")
            game = game.set_state(3)
        if 3 <= game.state < 4:
            # Force a discard if player has too many cards left
            current_player = game.current_player()
            if len(current_player.hand.cards_in_hand) > MAX_CARDS_IN_HAND:
                if game.state == 3:
                    logger.debug(f"{current_player.index} Must discard")
                    discard_options = get_discard_options(player=current_player)
                    return current_player, game.set_state(3.5), tuple(), discard_options, game.winner() is not None
                if game.state == 3.5:
                    actions = ((current_player, None, action),)
                    logger.debug(f"{current_player.index} Discards {action}")
                    game = execute_actions(game, actions, debug=debug)

            game = game.end_turn()
            logger.debug(f"{current_player.index} Ends turn")
            actions = tuple()  # Reset actions in case there were discards
            game = game.set_state(0)
            if len(game.game_deck) == 0:
                logger.warning("Out of cards")
                break
    return game.winner(), game, None, None, True
