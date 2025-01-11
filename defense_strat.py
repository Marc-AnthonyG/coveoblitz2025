from game_message import Character, TeamGameState, TileType
from util import is_in_our_zone


def should_defense(character: Character, game_message: TeamGameState) -> bool:
    """
    This return True if the character can eat someone in the next turn
    """
    if not is_in_our_zone(game_message.currentTeamId, character.position, game_message.teamZoneGrid):
        return False

    for enemy in game_message.otherCharacters:
        deltaX = enemy.position.x - character.position.x
        deltaY = enemy.position.y - character.position.y
        if abs(deltaX) <= 1 and abs(deltaY) <= 1:
            return True

def defense(character: Character, game_message: TeamGameState):
    """
    This function try to decide how to move to eat the enemy
    """
    closest_enemy = None

    for enemy in game_message.otherCharacters:
        deltaX = enemy.position.x - character.position.x
        deltaY = enemy.position.y - character.position.y
        if abs(deltaX) <= 1 and abs(deltaY) <= 1:
            closest_enemy = enemy

    # Should not happen
    if closest_enemy is None:
        return None

    possible_move = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    possible_enemy_move = []
    for move in possible_move:
        new_x = closest_enemy.position.x + move[0]
        new_y = closest_enemy.position.y + move[1]

        if game_message.map.tiles[new_x][new_y] != TileType.WALL:
            possible_enemy_move.append((closest_enemy.position.x + move[0], closest_enemy.position.y + move[1]))
