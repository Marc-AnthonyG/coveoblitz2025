import heapq
from typing import List

import game_message
import util
from game_message import Character, TeamGameState


def check_if_move_is_doable(character: Character, game_message: game_message.TeamGameState, actions: List[game_message.Action]) -> List[game_message.Action]:
    action_to_play: List[game_message.Action] = []

    for action in actions:
        if action.type == "MOVE_TO":
            move_to_position: game_message.Position = action.position
            if util.is_not_in_enemies_zone(game_message.teamIds, game_message.currentTeamId, move_to_position, game_message.teamZoneGrid) \
                and util.is_not_in_enemies_zone(game_message.teamIds, game_message.currentTeamId, character.position, game_message.teamZoneGrid):


    else:
        action_to_play.append(action)

    return action_to_play

def a_star_enemy_detect(start: game_message.Position, goal: game_message.Position, game_message: TeamGameState) -> bool:
    tiles: List[List[game_message.TileType]] = game_message.map.tiles
    open_list: List[tuple[int, game_message.Position]] = []
    heapq.heappush(open_list, (0, start))  # (priority, position)

    g_score = {start: 0}
    f_score = {start: util.manhattan_distance(start, goal)}

    visited = set()

    while open_list:
        _, current = heapq.heappop(open_list)

        if game_message.teamZoneGrid[current.x][current.y]:
            return False

        if current == goal:
            return True

        visited.add(current)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = game_message.Position(current.x + dx, current.y + dy)

            if tiles[neighbor.x][neighbor.y] == game_message.TileType.EMPTY and neighbor not in visited:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + util.manhattan_distance(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

    # If the goal cannot be reached
    return False