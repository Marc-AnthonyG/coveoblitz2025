from game_message import *
from util import is_not_in_enemies_zone, is_in_enemies_zone
from collections import deque

def choose_to_pickup_or_deposit(character: Character, game_state: TeamGameState) -> list[Action]:
    if len(character.carriedItems) > 0 and character.carriedItems[-1].value < 0:
        # choosing to deposit
        return depositTrash(character, game_state)
    return pickupTrash(character, game_state)


def pickupTrash(character: Character, game_state: TeamGameState) -> list[Action]:
    for item in game_state.items:
        if item.position == character.position and item.value < 0:
            return [GrabAction(character.id)]
        if item.value < 0 and is_not_in_enemies_zone(game_state.teamIds, game_state.currentTeamId, item.position, game_state.teamZoneGrid):
            return [SetSkinAction(character.id, 3),
            MoveToAction(character.id, Position(item.position.x, item.position.y))]


def depositTrash(character: Character, game_state: TeamGameState) -> list[Action]:
    if is_in_enemies_zone(game_state.teamIds, game_state.currentTeamId, character.position, game_state.teamZoneGrid) and game_state.map.tiles[character.position.x][character.position.y] == TileType.EMPTY:
        return [DropAction(character.id)]


    start_position = character.position
    queue = deque([start_position])
    visited = set()
    visited.add((start_position.x, start_position.y))

    while queue:
        current_position = queue.popleft()
        if is_in_enemies_zone(game_state.teamIds, game_state.currentTeamId, current_position, game_state.teamZoneGrid):
            return [MoveToAction(character.id, Position(current_position.x, current_position.y))]
        adjacent_positions = [
                Position(current_position.x + 1, current_position.y),
                Position(current_position.x - 1, current_position.y),
                Position(current_position.x, current_position.y + 1),
                Position(current_position.x, current_position.y - 1)
            ]
        adjacent_positions = [pos for pos in adjacent_positions if 0 <= pos.x < game_state.map.width and 0 <= pos.y < game_state.map.height and game_state.map.tiles[pos.x][pos.y] == TileType.EMPTY]
        (game_state.map.width, game_state.map.height)
        for neighbor in adjacent_positions:
                
            if (neighbor.x, neighbor.y) not in visited:
                visited.add((neighbor.x, neighbor.y))
                queue.append(neighbor)

    return []