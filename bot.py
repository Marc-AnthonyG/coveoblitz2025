import random
from typing import Dict
from game_message import *
from attack import choose_to_pickup_or_deposit
import retrieve_closest_resource as rcr


class Bot:
    def __init__(self):
        self.current_state : Dict[str, rcr.strategy_state] = {}
        print("Initializing your super mega duper bot")

    def get_next_move(self, game_message: TeamGameState):
        if (len(self.current_state) == 0):
            for character in game_message.yourCharacters:
                self.current_state[character.id] = rcr.strategy_state.RETRIEVE_CLOSEST_RESOURCE
        
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []
        actions += choose_to_pickup_or_deposit(game_message.yourCharacters[0], game_state=game_message)

        # for character in game_message.yourCharacters:
        #     move, next_state = rcr.make_a_move(self.current_state[character.id], character, game_message)
        #     self.current_state[character.id] = next_state
        #     actions.append(move)
        # You can clearly do better than the random actions above! Have fun!
        return actions
