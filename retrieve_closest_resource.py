from enum import Enum
from typing import Optional, Tuple
import game_message
import util

class strategy_state(Enum):
    RETRIEVE_CLOSEST_RESOURCE = 1
    STACK_RESOURCES = 2
    BRING_RESOURCE_TO_BASE = 3
    PICKUP_TRASH = 4
    DEPOSIT_TRASH = 5
        
    
def make_a_move(current_state : strategy_state, character : game_message.Character, game_message_: game_message.TeamGameState)->Tuple[Optional[game_message.Action], strategy_state]:
    if not character.alive:
        return (game_message.MoveDownAction(characterId=character.id), strategy_state.RETRIEVE_CLOSEST_RESOURCE)
    elif current_state.value == strategy_state.RETRIEVE_CLOSEST_RESOURCE.value:
        return retrieve_closest_resource(character, game_message_)
    elif current_state.value == strategy_state.STACK_RESOURCES.value:
        if should_car_go_back_home(character, game_message_):
            return bring_resource_to_base(character, game_message_)
        else:
            return retrieve_closest_resource(character, game_message_)
    else:
        return bring_resource_to_base(character, game_message_)



def find_closest_resource(character : game_message.Character, game_message_: game_message.TeamGameState) -> Optional[game_message.Item]:
    current_position : game_message.Position = character.position
    max_score : float = -1000000
    closest_resource : Optional[game_message.Item] = None
    for resource  in game_message_.items:
        if (resource.type[0] != "b"):
            continue
        
        if is_tile_from_our_zone(resource.position, game_message_):
            continue
        
        dist : Optional[float] = find_distance(current_position, resource.position, game_message_)
        if (dist is None):
            continue
        resource_value : int = resource.value
        score : float = compute_resource_value(dist, resource_value, game_message_)
        if (score > max_score):
            max_score = dist
            closest_resource = resource
        
    return closest_resource

def compute_resource_value(distance_to_car : float, resource_value : int, game_message_: game_message.TeamGameState)->float:
    return -distance_to_car

def sum_adjactent_resources(position : game_message.Position, game_message_: game_message.TeamGameState)->int:
    min_x : int = max(0, position.x - 1)
    max_x : int = min(game_message_.map.width, position.x + 1)
    min_y : int = max(0, position.y - 1)
    max_y : int = min(game_message_.map.height, position.y + 1)
    sum_ : int = 0
    #check adjactent tiles
    for x in range(min_x, max_x):
        for y in range(min_y, max_y):
            if is_tile_empty(game_message.Position(x,y), game_message_):
                continue
            for item in game_message_.items:
                if item.type[0] != "b":
                    continue
                if item.position == position:
                    sum_ += item.value
    return sum_

def is_tile_from_our_zone(position : game_message.Position, game_message_: game_message.TeamGameState)->bool:
    return game_message_.teamZoneGrid[position.x][position.y] == game_message_.currentTeamId
     
def find_distance(position1 : game_message.Position, position2 : game_message.Position, game_message_: game_message.TeamGameState)->Optional[float]:
    return util.a_star(position1, position2, game_message_.map.tiles)

def should_car_go_back_home(character : game_message.Character, game_message_: game_message.TeamGameState)->bool:
    if (character.numberOfCarriedItems == 0):
        return False
    if (character.numberOfCarriedItems == game_message_.constants.maxNumberOfItemsCarriedPerCharacter):
        return True
    
    home_tile = find_closest_available_teamtile(character, game_message_)
    closest_resource = find_closest_resource(character, game_message_)
    
    if (closest_resource is None):
        return True
    elif (home_tile is None):
        return False
    dist_home = find_distance(character.position, home_tile, game_message_)
    if dist_home is None:
        return False
    dist_resource = find_distance(character.position, home_tile, game_message_)
    if dist_resource is None:
        return True
     
    elif (dist_home < dist_resource):
        return True
    return False

def retrieve_closest_resource(character : game_message.Character, game_message_: game_message.TeamGameState):
    item : Optional[game_message.Item] = find_closest_resource(character, game_message_)
    
    if item is not None:
        if item.position == character.position:
            return game_message.GrabAction(characterId=character.id), strategy_state.STACK_RESOURCES
        else:
            return game_message.MoveToAction(characterId=character.id, position=item.position), strategy_state.RETRIEVE_CLOSEST_RESOURCE
    return (None, strategy_state.RETRIEVE_CLOSEST_RESOURCE)

def find_closest_available_teamtile(character : game_message.Character, game_message_: game_message.TeamGameState)->Optional[game_message.Position]:
    current_position : game_message.Position = character.position
    min_distance : float = 10000000
    closest_teamtile : Optional[game_message.Position] = None
    for x in range(len(game_message_.teamZoneGrid)):
        for y in range(len(game_message_.teamZoneGrid[0])):
            tile_position = game_message.Position(x,y)
            if not is_tile_from_our_zone(position=tile_position, game_message_=game_message_):
                continue
            
            dist : Optional[float] = find_distance(current_position, tile_position, game_message_)
            if (dist is None):
                continue
            if (dist < min_distance and is_tile_empty(tile_position, game_message_)):
                min_distance = dist
                closest_teamtile = tile_position
    return closest_teamtile

def is_tile_empty(position : game_message.Position, game_message_: game_message.TeamGameState)->bool:
    is_wall : bool = game_message_.map.tiles[position.x][position.y].value == "WALL"
    if (is_wall):
        return False
    
    for item in game_message_.items:
        if item.position == position:
            return False
    return True

def bring_resource_to_base(character : game_message.Character, game_message_: game_message.TeamGameState):
    position : Optional[game_message.Position] = find_closest_available_teamtile(character, game_message_)
    if position is not None:
        if (position == character.position):
            if (character.numberOfCarriedItems == 1):
                return game_message.DropAction(characterId=character.id), strategy_state.RETRIEVE_CLOSEST_RESOURCE            
            return game_message.DropAction(characterId=character.id), strategy_state.BRING_RESOURCE_TO_BASE
        else:
            return game_message.MoveToAction(characterId=character.id, position=position), strategy_state.BRING_RESOURCE_TO_BASE
    else:
        return (None, strategy_state.BRING_RESOURCE_TO_BASE)