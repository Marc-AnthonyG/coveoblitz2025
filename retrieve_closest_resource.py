from collections import deque
from enum import Enum
from typing import Optional, Tuple, Deque
import game_message
import util
import random
class strategy_state(Enum):
    RETRIEVE_CLOSEST_RESOURCE = 1
    STACK_RESOURCES = 2
    BRING_RESOURCE_TO_BASE = 3
    PICKUP_TRASH = 4
    DEPOSIT_TRASH = 5
        
    
def make_a_move(current_state : strategy_state, character : game_message.Character, game_message_: game_message.TeamGameState)->Tuple[Optional[game_message.Action], strategy_state, Optional[game_message.Position]]:
    if current_state == strategy_state.RETRIEVE_CLOSEST_RESOURCE:
        return retrieve_closest_resource(character, game_message_)
    elif current_state == strategy_state.STACK_RESOURCES:
        if should_car_go_back_home(character, game_message_):
            return bring_resource_to_base(character, game_message_)
        else:
            return retrieve_closest_resource(character, game_message_)
    else:
        return bring_resource_to_base(character, game_message_)



def find_closest_resource(character : game_message.Character, game_message_: game_message.TeamGameState) -> Tuple[Optional[game_message.Item],float]:
    current_position : game_message.Position = character.position
    min_dist : float = 1000000
    closest_resource : Optional[game_message.Item] = None
    for resource  in game_message_.items:
        if (resource.type[0] != "b"):
            continue
        
        if is_tile_from_our_zone(resource.position, game_message_):
            continue
        
        dist : Optional[float] = find_distance(current_position, resource.position, game_message_)
        if (dist is None):
            continue
        if (dist < min_dist):
            min_dist = dist
            closest_resource = resource
    return closest_resource, min_dist

def compute_resource_value(distance_to_car : float, resource_value : int, game_message_: game_message.TeamGameState)->float:
    return -distance_to_car

def is_tile_from_our_zone(position : game_message.Position, game_message_: game_message.TeamGameState)->bool:
    return game_message_.teamZoneGrid[position.x][position.y] == game_message_.currentTeamId
     
def find_distance(position1 : game_message.Position, position2 : game_message.Position, game_message_: game_message.TeamGameState)->Optional[float]:
    return util.a_star(position1, position2, game_message_.map.tiles)

def should_car_go_back_home(character : game_message.Character, game_message_: game_message.TeamGameState)->bool:
    if (character.numberOfCarriedItems == 0):
        return False
    if (character.numberOfCarriedItems == game_message_.constants.maxNumberOfItemsCarriedPerCharacter):
        return True
    
    home_tile, dist_home = find_closest_available_teamtile(character, game_message_)
    closest_resource, dist_resource = find_closest_resource(character, game_message_)
    
    if (closest_resource is None):
        return True
    elif (home_tile is None):
        return False
    elif (dist_home < dist_resource):
        return True
    return False

def retrieve_closest_resource(character : game_message.Character, game_message_: game_message.TeamGameState) -> Tuple[Optional[game_message.Action], strategy_state, Optional[game_message.Position]]:
    item, _ = find_closest_resource(character, game_message_)
    
    if item is not None:
        if item.position == character.position:
            return game_message.GrabAction(characterId=character.id), strategy_state.STACK_RESOURCES, item.position
        else:
            return game_message.MoveToAction(characterId=character.id, position=item.position), strategy_state.RETRIEVE_CLOSEST_RESOURCE, item.position
    return (None, strategy_state.PICKUP_TRASH, None)

def find_closest_available_teamtile(character : game_message.Character, game_message_: game_message.TeamGameState)->Tuple[Optional[game_message.Position], float]:
    start_position = character.position
    queue: Deque[tuple[game_message.Position, int]]= deque([(start_position, 0)])  # (x, y, distance)
    visited = set()
    visited.add((start_position.x, start_position.y))

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        position, dist = queue.popleft()
        x = position.x
        y = position.y

        if util.is_in_our_zone(game_message_.currentTeamId, position, game_message_.teamZoneGrid) and is_tile_empty(position, game_message_, character.id):
            return position, dist


        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if game_message_.map.tiles[nx][ny] != game_message.TileType.WALL:
                visited.add((nx, ny))
                queue.append((game_message.Position(nx, ny), dist + 1))

    return None, -1


def is_tile_empty(position : game_message.Position, game_message_: game_message.TeamGameState, id :str)->bool:
    is_wall : bool = game_message_.map.tiles[position.x][position.y].value == "WALL"
    if (is_wall):
        return False
    
    for friendly_character in game_message_.yourCharacters:
        if friendly_character.id == id:
            continue
        if friendly_character.position == position:
            return random.choice([True, False])
    for item in game_message_.items:
        if item.position == position:
            return False
    return True

def bring_resource_to_base(character : game_message.Character, game_message_: game_message.TeamGameState) -> Tuple[Optional[game_message.Action], strategy_state, Optional[game_message.Position]]:
    position , _ = find_closest_available_teamtile(character, game_message_)
    if position is not None:
        if (position == character.position):
            if (character.numberOfCarriedItems == 1):
                return game_message.DropAction(characterId=character.id), strategy_state.PICKUP_TRASH, position          
            return game_message.DropAction(characterId=character.id), strategy_state.BRING_RESOURCE_TO_BASE, position
        else:
            return game_message.MoveToAction(characterId=character.id, position=position), strategy_state.BRING_RESOURCE_TO_BASE, position
    else:
        return (None, strategy_state.BRING_RESOURCE_TO_BASE, None)