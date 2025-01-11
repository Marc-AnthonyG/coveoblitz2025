import random
from collections import deque
from typing import List, Deque, Optional

import util
from skin_const import DEFENCE_SKIN_INDEX
from game_message import Character, TeamGameState, TileType, SetSkinAction, MoveToAction, Position, Action
from util import is_in_our_zone


def can_tag_close_enemy(character: Character, game_message: TeamGameState) -> bool:
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

def try_to_tag_close_enemy(character: Character, game_message: TeamGameState) -> List[Action]:
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
            possible_enemy_move.append(Position(x=closest_enemy.position.x + move[0], y=closest_enemy.position.y + move[1]))


    possible_our_move = []
    for move in possible_enemy_move:
        if abs(move.x - character.position.x) + abs(move.y - character.position.y) <= 1:
            possible_our_move.append(move)

    if len(possible_our_move) == 0:
        return []
    else:
        random_move = possible_our_move[random.randint(0, len(possible_our_move) - 1)]
        return [SetSkinAction(characterId=character.id, skinIndex=DEFENCE_SKIN_INDEX), MoveToAction(characterId=character.id, position=random_move)]


def create_pair_of_intercepter(game_message: TeamGameState) -> list[Action]:
    """
    This function create a pair of intercepter
    """
    enemy_with_resource_in_our_zone = []
    for enemy in game_message.otherCharacters:
        if is_in_our_zone(game_message.currentTeamId, enemy.position, game_message.teamZoneGrid):
            if enemy.has_item:
                enemy_with_resource_in_our_zone.append(enemy)

    list_of_actions = []

    for enemy in enemy_with_resource_in_our_zone:
        exit_position, dist = get_exit_position(enemy.position, game_message, game_message.currentTeamId)
        if exit_position is None:
            continue

        for character in game_message.yourCharacters:
            if util.manhattan_distance(character.position, exit_position) <= dist:
                a_star_dist = util.a_star(character.position, exit_position, game_message.map.tiles)
                if a_star_dist is not None and a_star_dist <= dist:
                    list_of_actions.append(MoveToAction(character.id, exit_position))
                    continue

    return list_of_actions

def get_exit_position(starting_position: Position, game_message: TeamGameState, goalTeamId: str, ) -> tuple[Optional[Position], int]:
    """
    Return the exit position of the bot
    """
    starting_team_id = game_message.teamZoneGrid[starting_position.x][starting_position.y]
    queue: Deque[tuple[Position, Optional[Position], int]] = deque([(starting_position, None, 0)]) # (Position, exit_position | None, dist)
    visited = {starting_position}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        current_position, exit_position, dist = queue.popleft()
        x = current_position.x
        y = current_position.y

        # Stop searching when you get to enemy zone
        if game_message.teamZoneGrid[x][y] == goalTeamId:
            return exit_position, dist

        # Explore adjacent tiles
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if game_message.map.tiles[nx][ny] != TileType.WALL:
                visited.add(Position(nx, ny))
                if game_message.teamZoneGrid[nx][ny] != starting_team_id:
                    queue.append((Position(nx, ny), current_position, dist+1))
                else:
                    queue.append((Position(nx, ny), exit_position, dist+1))

    return None, 0
