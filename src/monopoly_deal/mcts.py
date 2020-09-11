from mcts import mcts
from typing import List, Dict

from monopoly_deal.actions import Action
from monopoly_deal.agents import Agent, RandomAgent
from monopoly_deal.cards import Card
from monopoly_deal.game import Game, Player
from monopoly_deal.play import step


class State:
    def __init__(self, ai_player: Player, player: Player, game: Game, actions: List, available_actions: Dict):
        self.ai_player = ai_player
        self.game = game
        self.player = player
        self.actions = actions
        self.available_actions = available_actions

    def getCurrentPlayer(self):
        if self.player.index == self.ai_player.index:
            return 1
        else:
            return -1

    def getPossibleActions(self):
        possible_actions = []
        for card, list_of_actions in self.available_actions.items():
            for action in list_of_actions:
                possible_actions.append((card, action))
        return possible_actions

    def takeAction(self, action):
        card, action = action
        try:
            player, game, actions, available_actions, is_over = step(
                game=self.game,
                actions=self.actions,
                card_to_play=card,
                action=action
            )
        except Exception:
            import ipdb;
            ipdb.set_trace()

        return State(
            ai_player=self.ai_player,
            player=player,
            game=game,
            actions=actions,
            available_actions=available_actions
        )

    def isTerminal(self):
        return self.game.winner() is not None

    def getReward(self):
        winner = self.game.winner()
        if winner.index == self.ai_player.index:
            return 1
        else:
            return -1


class MCTSAgent(Agent):
    def __init__(self, player: Player, time_limit: int):
        self.player = player
        self.mcts = mcts(timeLimit=time_limit)

    def get_response(self, game: Game, actions: List[Action], available_responses: Dict[Card, List[Action]]):
        card, action = self.mcts.search(initialState=State(ai_player=self.player, player=game.players[self.player.index], game=game, actions=actions, available_actions=available_responses))
        return card, action

    def get_discard_action(self, game: Game, actions: List[Action], discard_options: Dict[Card, List[Action]]):
        card, action = self.mcts.search(
            initialState=State(ai_player=self.player, player=game.players[self.player.index], game=game, actions=actions,
                               available_actions=discard_options))
        return card, action

    def get_action(self, game: Game, actions: List[Action], available_actions: Dict[Card, List[Action]]):
        card, action = self.mcts.search(
            initialState=State(ai_player=self.player, player=game.players[self.player.index], game=game, actions=actions,
                               available_actions=available_actions))
        return card, action
