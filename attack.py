from game_message import *
from util import is_not_in_enemies_zone
from collections import deque

def choose_to_pickup_or_deposit(character: Character, game_state: TeamGameState) -> list[Action]:
    if len(character.carriedItems) > 0 and character.carriedItems[-1].value < 0:
        # choosing to deposit
        print("depositing")
        return depositTrash(character, game_state)
    return pickupTrash(character, game_state)


def pickupTrash(character: Character, game_state: TeamGameState) -> list[Action]:
    for item in game_state.items:
        if item.value < 0 and is_not_in_enemies_zone(game_state.teamIds, game_state.currentTeamId, item.position, game_state.teamZoneGrid):
            return [SetSkinAction(character.id, 3),
            MoveToAction(character.id, item.position)]


def depositTrash(character: Character, game_state: TeamGameState) -> list[Action]:
    start_position = character.position
    queue = deque([start_position])
    visited = set()
    visited.add(start_position)

    while queue:
        current_position = queue.popleft()
        if is_not_in_enemies_zone(game_state.teamIds, game_state.currentTeamId, current_position, game_state.teamZoneGrid):
            return [MoveToAction(character.id, current_position)]

        for neighbor in game_state.get_neighbors(current_position):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return []