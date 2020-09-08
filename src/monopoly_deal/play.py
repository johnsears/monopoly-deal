import logging

from monopoly_deal.cards import *
from monopoly_deal.agents import RandomAgent
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
                elif isinstance(action, Discard):
                    game = game.discard_card(card=card)
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


def get_available_responses(player: Player, actions: List[Tuple[Player, Card, Action]]):
    available_responses = {None: [NoResponse()]}
    current_hand = player.hand
    for current_player, card_to_play, action in actions:
        if player.index == current_player.index and card_to_play is not None:
            current_hand = current_hand.play_card(card_to_play)

    opposing_player, cards_to_play, action = actions[-1]
    if isinstance(action, Charge):
        available_payment_options = []
        # If wipes them out, give everything
        if action.amount >= player.board.get_total_value():
            pay = Pay(
                pay_to_player=opposing_player,
                cash_cards=player.board.cash_cards,
                property_cards=player.board.get_all_property_cards()
            )
            available_payment_options.append(pay)
        else:
            # Try paying with largest bills first
            cash_cards_to_pay = player.board.find_cash_to_pay_bill_up_to_amount(bill_amount=action.amount)
            cash_value = sum([card.value for card in cash_cards_to_pay])
            if cash_value == action.amount:
                pay = Pay(pay_to_player=opposing_player, cash_cards=tuple(cash_cards_to_pay), property_cards=tuple())
                available_payment_options.append(pay)
            else:
                payment_options = player.board.find_additional_cards_to_pay_bill(
                    bill_amount=action.amount,
                    cards_in_payment=cash_cards_to_pay
                )
                for payment_set in payment_options:
                    cash_cards: Tuple[Cashable] = tuple([card for card in payment_set if isinstance(card, Cashable)])
                    property_cards = tuple([card for card in payment_set if isinstance(card, PropertyCard)])
                    pay = Pay(pay_to_player=opposing_player, cash_cards=cash_cards, property_cards=property_cards)
                    available_payment_options.append(pay)
        if available_payment_options:
            available_responses[None] = available_payment_options
    for card in current_hand.cards_in_hand:
        if isinstance(card, ActionCard):
            if card.action_type == ActionType.JUST_SAY_NO:
                available_responses[card] = [SayNo(to_player=opposing_player)]
                break
    return available_responses


def play_game():
    game = new_game(2)
    agents = {player.index: RandomAgent() for player in game.players}
    n_turns = 0
    while not game.winner():
        # print("New turn")
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
                # print("Ended turn")
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
        game = game.end_turn()
        n_turns += 1
        if n_turns > 250:
            break
