from typing import Dict, List

import defense_strat
from defense_strat import can_tag_close_enemy, try_to_tag_close_enemy
from game_message import *
from attack import choose_to_pickup_or_deposit
import retrieve_closest_resource as rcr
from weighted_map import WeightedMap, construct_weighted_map


class Bot:
    def __init__(self):
        self.current_state : Dict[str, Optional[rcr.strategy_state]] = dict()
        self.target_position_per_character : Dict[str, Optional[Position]] = dict()
        self.weight_map: Optional[WeightedMap] = None
        print("Initializing your super mega duper bot")

    def get_next_move(self, game_message: TeamGameState):
        if not self.weight_map:
            self.weight_map = construct_weighted_map(game_message)

        if (len(self.target_position_per_character) == 0):
            for character in game_message.yourCharacters:
                self.target_position_per_character[character.id] = None
                
        if (len(self.current_state) == 0):
            for i, character in enumerate(game_message.yourCharacters):
                if i % 2 == 1:
                    self.current_state[character.id] = rcr.strategy_state.PICKUP_TRASH
                else:
                    self.current_state[character.id] = rcr.strategy_state.RETRIEVE_CLOSEST_RESOURCE
                
        
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions: List[Action] = []

        defense_actions = defense_strat.long_distance_defence(game_message)

        for character in game_message.yourCharacters:
            character_actions: List[Action] = []

            defense_actions_of_character = [action for action in defense_actions if action.characterId == character.id]
            if len(defense_actions_of_character) > 0:
                character_actions += defense_actions_of_character
            if can_tag_close_enemy(character, game_message):
                character_actions += try_to_tag_close_enemy(character, game_message)

            if len(character_actions) == 0:
                if self.current_state[character.id] is None:
                    moves, target_position = choose_to_pickup_or_deposit(self, character, game_state=game_message)
                    character_actions+= moves
                    
                else:
                    move, next_state, target_position = rcr.make_a_move(self.current_state[character.id], character, game_message)
                    self.current_state[character.id] = next_state
                    self.target_position_per_character[character.id] = target_position
                    character_actions.append(move)

            actions += character_actions

        # You can clearly do better than the random actions above! Have fun!
        return actions
