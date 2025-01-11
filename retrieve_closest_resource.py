from enum import Enum
from typing import Optional, Tuple
import game_message

class strategy_state(Enum):
    RETRIEVE_CLOSEST_RESOURCE = 1
    BRING_RESOURCE_TO_BASE = 2
        
    
def make_a_move(current_state : strategy_state, character : game_message.Character, game_message_: game_message.TeamGameState)->Tuple[game_message.Action, strategy_state]:
    if current_state.value == strategy_state.RETRIEVE_CLOSEST_RESOURCE.value:
        return retrieve_closest_resource(character, game_message_)
    else:
        return bring_resource_to_base(character, game_message_)



def find_closest_resource(character : game_message.Character, game_message_: game_message.TeamGameState) -> Optional[game_message.Item]:
    current_position : game_message.Position = character.position
    min_distance : float = 10000000
    closest_resource : Optional[game_message.Item] = None
    for resource  in game_message_.items:
        if (resource.type[0] != "b"):
            continue
        
        if is_tile_from_our_zone(resource.position, game_message_):
            continue
        
        dist = find_distance(current_position, resource.position)
        
        if (dist < min_distance):
            min_distance = dist
            closest_resource = resource
        
    return closest_resource

def is_tile_from_our_zone(position : game_message.Position, game_message_: game_message.TeamGameState)->bool:
    return game_message_.teamZoneGrid[position.x][position.y] == game_message_.currentTeamId
     
def find_distance(position1 : game_message.Position, position2 : game_message.Position)->float:
    return ((position1.x - position2.x)**2 + (position1.y - position2.y)**2)**0.5

def retrieve_closest_resource(character : game_message.Character, game_message_: game_message.TeamGameState):
    item : Optional[game_message.Item] = find_closest_resource(character, game_message_)
    
    if item is not None:
        if item.position == character.position:
            return game_message.GrabAction(characterId=character.id), strategy_state.BRING_RESOURCE_TO_BASE
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
            
            dist = find_distance(current_position, tile_position)

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
            return game_message.DropAction(characterId=character.id), strategy_state.RETRIEVE_CLOSEST_RESOURCE
        else:
            return game_message.MoveToAction(characterId=character.id, position=position), strategy_state.BRING_RESOURCE_TO_BASE
    else:
        return (None, strategy_state.BRING_RESOURCE_TO_BASE)