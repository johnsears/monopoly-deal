import random

from typing import List, Dict

from monopoly_deal.actions import Action
from monopoly_deal.cards import Card
from monopoly_deal.game import Game


class RandomAgent:
    def get_action(self, game: Game, actions: List[Action], available_actions: Dict[Card, List[Action]]):
        card_to_play = random.choice(list(available_actions.keys()))
        try:
            action_to_happen = random.choice(available_actions[card_to_play])
        except Exception:
            print(available_actions)
            import ipdb; ipdb.set_trace()
        return card_to_play, action_to_happen

    def get_response(self, game: Game, actions: List[Action], available_responses: Dict[Card, List[Action]]):
        card_to_play = random.choice(list(available_responses.keys()))
        action_to_happen = random.choice(available_responses[card_to_play])
        return card_to_play, action_to_happen


