from typing import Dict
from game_message import *
from attack import choose_to_pickup_or_deposit
import retrieve_closest_resource as rcr
from weighted_map import WeightedMap, construct_weighted_map

FETCH_BLUE_INDEX = 1
RETRIEVE_BLUE_INDEX = 2
FETCH_RED_INDEX = 1
SEND_RED_INDEX = 2
DEFENCE_SKIN_INDEX = 5

class Bot:
    def __init__(self):
        self.current_state : Dict[str, rcr.strategy_state] = {}
        self.weight_map: WeightedMap | None = None
        print("Initializing your super mega duper bot")

    def get_next_move(self, game_message: TeamGameState):
        if not self.weight_map:
            self.weight_map = construct_weighted_map(game_message)

        if (len(self.current_state) == 0):
            for i, character in enumerate(game_message.yourCharacters):
                if i % 2 == 0:
                    self.current_state[character.id] = None
                else:
                    self.current_state[character.id] = rcr.strategy_state.RETRIEVE_CLOSEST_RESOURCE
                
        
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        for character in game_message.yourCharacters:
            if self.current_state[character.id] is None:
                actions += choose_to_pickup_or_deposit(character, game_state=game_message)
            else:
                move, next_state = rcr.make_a_move(self.current_state[character.id], character, game_message)
                self.current_state[character.id] = next_state
                actions.append(move)
        # You can clearly do better than the random actions above! Have fun!
        return actions
