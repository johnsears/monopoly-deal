import random

from abc import abstractmethod
from typing import List, Dict

from monopoly_deal.actions import Action
from monopoly_deal.cards import Card
from monopoly_deal.game import Game


class Agent:
    @abstractmethod
    def get_action(self, game: Game, actions: List[Action], available_actions: Dict[Card, List[Action]]):
        pass

    @abstractmethod
    def get_response(self, game: Game, actions: List[Action], available_responses: Dict[Card, List[Action]]):
        pass

    @abstractmethod
    def get_discard_action(self, game: Game, actions: List[Action], discard_options: List[Action]):
        pass


class RandomAgent(Agent):
    def get_action(self, game: Game, actions: List[Action], available_actions: Dict[Card, List[Action]]):
        card_to_play = random.choice(list(available_actions.keys()))
        action_to_happen = random.choice(available_actions[card_to_play])
        return card_to_play, action_to_happen

    def get_response(self, game: Game, actions: List[Action], available_responses: Dict[Card, List[Action]]):
        card_to_play = random.choice(list(available_responses.keys()))
        action_to_happen = random.choice(available_responses[card_to_play])
        return card_to_play, action_to_happen

    def get_discard_action(self, game: Game, actions: List[Action], discard_options: List[Action]):
        discard_choice = random.choice(discard_options)
        return None, discard_choice

