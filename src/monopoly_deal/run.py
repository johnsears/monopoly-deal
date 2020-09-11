from monopoly_deal.agents import RandomAgent
from monopoly_deal.mcts import MCTSAgent
from monopoly_deal.play import new_game, step


def sim_new_game(mcts_time_limit: int):
    game = new_game(2)
    agents = {player.index: RandomAgent() for player in game.players}
    agents[0] = MCTSAgent(player=game.players[0], time_limit=mcts_time_limit)

    # Play game
    player, game, actions, available_actions, is_over = step(game=game, actions=tuple(), card_to_play=None, action=None)
    while not is_over:
        card_to_play, action = agents[player.index].get_action(game=game, actions=actions, available_actions=available_actions)
        player, game, actions, available_actions, is_over = step(game=game, actions=actions, card_to_play=card_to_play, action=action, debug=False)
    return game


# Prove that MCTS is working
for time_limit in [10, 50, 100, 500]:
    print(f"Time limit {time_limit}ms for MCTS Agent.")
    wins = 0
    for _ in range(10):
       game = sim_new_game(mcts_time_limit=time_limit)
       if game.winner().index == 0:
           wins += 1
    print(f'MCTS Agent won {wins} times')
