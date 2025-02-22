import heapq
from typing import List, Optional
import game_message
from game_message import Position


def is_in_our_zone(current_team_id: str, position: game_message.Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.x][position.y] == current_team_id

def is_not_in_enemies_zone(teamIds: list[str], current_team_id: str, position: game_message.Position,  teamZoneGrid: list[list[str]]) -> bool:
    return not is_in_enemies_zone(teamIds, current_team_id, position, teamZoneGrid)

def is_in_enemies_zone(teamIds: list[str], current_team_id: str, position: game_message.Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.x][position.y] in teamIds and teamZoneGrid[position.x][position.y] != current_team_id

def a_star(start: game_message.Position, goal: game_message.Position, tiles: List[List[game_message.TileType]]) -> Optional[int]:
    open_list: List[tuple[int, Position]] = []
    heapq.heappush(open_list, (0, start))  # (priority, position)

    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}

    visited = set()

    while len(open_list) > 0:
        _, current = heapq.heappop(open_list)

        if current == goal:
            return g_score[current]

        visited.add(current)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = game_message.Position(current.x + dx, current.y + dy)

            if tiles[neighbor.x][neighbor.y] == game_message.TileType.EMPTY and neighbor not in visited:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

    # If the goal cannot be reached
    return None

def find_first_move(start: game_message.Position, goal: game_message.Position, tiles: List[List[game_message.TileType]]) -> Optional[Position]:
    open_list: List[tuple[int, Position, Optional[Position]]] = []
    heapq.heappush(open_list, (0, start, None))  # (priority, position, first_move_position)

    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}

    visited = set()

    while len(open_list) > 0:
        _, current, first_move = heapq.heappop(open_list)

        if current == goal:
            return first_move

        visited.add(current)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = game_message.Position(current.x + dx, current.y + dy)

            if tiles[neighbor.x][neighbor.y] == game_message.TileType.EMPTY and neighbor not in visited:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal)
                    if first_move is None:
                        heapq.heappush(open_list, (f_score[neighbor], neighbor, neighbor))
                    else:
                        heapq.heappush(open_list, (f_score[neighbor], neighbor, first_move))

    # If the goal cannot be reached
    return None

def manhattan_distance(pos1: game_message.Position, pos2: game_message.Position) -> int:
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
