from typing import Dict, List

import defense_strat
from defense_strat import can_tag_close_enemy, try_to_tag_close_enemy
from game_message import *
from attack import choose_to_pickup_or_deposit
import retrieve_closest_resource as rcr
from util import find_first_move
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

        defense_actions = []

        if len(game_message.teamIds) == 2:
            defense_actions = defense_strat.long_distance_defence(game_message)

        for character in game_message.yourCharacters:
            print(f"Choosing move for character id: {character.id}")
            character_actions: List[Action] = []
            if not character.alive:
                self.current_state[character.id] = rcr.strategy_state.PICKUP_TRASH
                print(f"Character is not alive")
                continue
            defense_actions_of_character = [action for action in defense_actions if action.characterId == character.id]
            if len(defense_actions_of_character) > 0:
                print(f"Character is long blocking")
                character_actions.append(defense_actions_of_character[0])
            elif can_tag_close_enemy(character, game_message):
                print(f"Character is short blocking")
                character_actions += try_to_tag_close_enemy(character, game_message)

            if len(character_actions) == 0:
                if self.current_state[character.id] == rcr.strategy_state.PICKUP_TRASH or self.current_state[character.id] == rcr.strategy_state.DEPOSIT_TRASH:
                    print(f"Character is trash man")
                    moves, target_position = choose_to_pickup_or_deposit(self, character, game_state=game_message)
                    character_actions+= moves
                    item_to_remove : Optional[Item] = None
                    if (target_position is not None):
                        for trash in game_message.items:
                            if trash.position == target_position:
                                item_to_remove = trash
                        
                        if item_to_remove is not None:
                            game_message.items.remove(item_to_remove)
                                        
                else:
                    print(f"Character is blitzing")
                    move, next_state, target_position = rcr.make_a_move(self.current_state[character.id], character, game_message)
                    self.current_state[character.id] = next_state
                    if move is None:
                        moves, target_position = choose_to_pickup_or_deposit(self, character, game_message)
                        character_actions+= moves
                    if (target_position is not None):
                        item_to_remove : Optional[Item] = None
                        for resource in game_message.items:
                            if resource.position == target_position:
                                item_to_remove = resource
                        
                        if item_to_remove is not None:
                            game_message.items.remove(item_to_remove)
                    
                    self.target_position_per_character[character.id] = target_position
                    if move is not None:
                        if move.type == "MOVE_TO":
                            for enemy in game_message.otherCharacters:
                                if game_message.teamZoneGrid[enemy.position.x][enemy.position.y] == enemy.teamId:
                                    game_message.map.tiles[enemy.position.x][enemy.position.y] = TileType.WALL
                            move.position = find_first_move(character.position, move.position, game_message.map.tiles)    
                            
                        character_actions.append(move)

            actions += character_actions

        print(f"Actions: {actions}")
        # You can clearly do better than the random actions above! Have fun!
        return actions
