from collections import deque
from enum import Enum
from typing import List, Dict, Tuple
from game_message import Position, TeamGameState, Threat, TileType
import heapq

from game_message import MoveLeftAction, MoveDownAction, MoveRightAction, MoveUpAction


class Branch(str, Enum):
    LEFT = ("LEFT",)
    RIGHT = ("RIGHT",)
    UP = ("UP",)
    DOWN = ("DOWN",)
    DONTMOVE = ("DONTMOVE",)
    UNKNOWN = ("UNKNOWN",)


class TileScores:
    branch: Branch = Branch.UNKNOWN
    score: float = -1
    visited: bool = False
    turn: int = 0


def marc(game_message: TeamGameState,
         weight_map: List[List[float]], active_threats: List[Threat], bot_tick_to_move: int, time_to_move: int, graph: Dict[Position, List[Tuple[Position, int]]]) -> MoveLeftAction | MoveRightAction | MoveUpAction | MoveDownAction | None:
    tiles_scores = construct_map_tilings_scores(game_message, active_threats, bot_tick_to_move, time_to_move)
    start_position = game_message.yourCharacter.position

    max_score = -1
    best_tile: TileScores = tiles_scores[start_position.x][start_position.y]

    for node in graph:
        x, y = node.x, node.y
        if tiles_scores[x][y].score > 0 and tiles_scores[x][y].score > max_score:
            max_score = tiles_scores[x][y].score
            best_tile = tiles_scores[x][y]

    if best_tile.score <= 0:
        for i in range(len(tiles_scores)):
            for j in range(len(tiles_scores[i])):
                new_score = tiles_scores[i][j].score * weight_map[i][j]
                if new_score > 0 and new_score > max_score:
                    max_score = new_score
                    best_tile = tiles_scores[i][j]

    if best_tile.branch == Branch.LEFT:
        return MoveLeftAction()
    elif best_tile.branch == Branch.RIGHT:
        return MoveRightAction()
    elif best_tile.branch == Branch.UP:
        return MoveUpAction()
    elif best_tile.branch == Branch.DOWN:
        return MoveDownAction()
    elif best_tile.branch == Branch.DONTMOVE:
        return None
    else:
        raise Exception("Unknown branch")


def construct_map_tilings_scores(game_message: TeamGameState, active_threats: List[Threat], bot_tick_speed: int, time_to_move: int) -> List[List[TileScores]]:
    tiles: List[List[TileType]] = game_message.map.tiles

    tiles_scores: List[List[TileScores]] = [[TileScores() for _ in range(game_message.map.height)] for _ in
                                            range(game_message.map.width)]

    start_position = game_message.yourCharacter.position
    tiles_scores[start_position.x][start_position.y].score = find_closest_threats(start_position, active_threats, tiles, 1, bot_tick_speed, time_to_move)
    tiles_scores[start_position.x][start_position.y].visited = True
    tiles_scores[start_position.x][start_position.y].branch = Branch.DONTMOVE

    queue: deque[Position] = deque([])
    if tiles[start_position.x - 1][start_position.y] != TileType.WALL:
        tiles_scores[start_position.x - 1][start_position.y].branch = Branch.LEFT
        tiles_scores[start_position.x - 1][start_position.y].turn = 1
        queue.append(Position(start_position.x - 1, start_position.y))
    if tiles[start_position.x + 1][start_position.y] != TileType.WALL:
        tiles_scores[start_position.x + 1][start_position.y].branch = Branch.RIGHT
        tiles_scores[start_position.x + 1][start_position.y].turn = 1
        queue.append(Position(start_position.x + 1, start_position.y))
    if tiles[start_position.x][start_position.y - 1] != TileType.WALL:
        tiles_scores[start_position.x][start_position.y - 1].branch = Branch.UP
        tiles_scores[start_position.x][start_position.y - 1].turn = 1
        queue.append(Position(start_position.x, start_position.y - 1))
    if tiles[start_position.x][start_position.y + 1] != TileType.WALL:
        tiles_scores[start_position.x][start_position.y + 1].branch = Branch.DOWN
        tiles_scores[start_position.x][start_position.y + 1].turn = 1
        queue.append(Position(start_position.x, start_position.y + 1))

    def is_valid_position(pos: Position) -> bool:
        return (0 <= pos.x < game_message.map.height and
                0 <= pos.y < game_message.map.width and
                tiles[pos.x][pos.y] == TileType.EMPTY)

    def process_neighbor(neighbor: Position, current_score: TileScores, additional_turns: int):
        if not is_valid_position(neighbor):
            return

        neighbor_score = tiles_scores[neighbor.x][neighbor.y]
        if neighbor_score.visited:
            return

        neighbor_score.branch = current_score.branch
        neighbor_score.turn = current_score.turn + additional_turns
        queue.append(neighbor)

    while queue:
        node: Position = queue.popleft()
        tiles_score = tiles_scores[node.x][node.y]

        if not tiles_score.visited:
            tiles_score.score = find_closest_threats(node, active_threats, tiles, tiles_score.turn, bot_tick_speed, time_to_move)
            tiles_score.visited = True

            if tiles_score.score <= 0:
                continue
            else:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    neighbor = Position(node.x + dx, node.y + dy)
                    process_neighbor(neighbor, tiles_score, 1)

    return tiles_scores


def find_closest_threats(position: Position, threats: List[Threat], tiles: List[List[TileType]], turn: int, tick_between_move: int, tick_before_next_move: int) -> float:
    min_tick_distance = None
    distances = []
    for threat in threats:
        manhattan_tick_distance_threat = (tick_before_next_move + (manhattan_distance(position, threat.position) - 1) * tick_between_move) - turn
        if min_tick_distance is not None and manhattan_tick_distance_threat >= min_tick_distance:
            distances.append(manhattan_tick_distance_threat)
            continue
        a_star_distance = a_star(position, threat.position, tiles)
        if a_star_distance is None:
            continue
        real_tick_distance = (tick_before_next_move + (a_star_distance - 1) * tick_between_move) - turn
        distances.append(real_tick_distance)
        if min_tick_distance is None or real_tick_distance < min_tick_distance:
            min_tick_distance = real_tick_distance

    if min_tick_distance is None:
        return -1
    else:
        distances.sort()
        if len(distances) >= 1 and distances[0] <= 0:
            return distances[0]
        return sum(distances[:3]) / 3


def manhattan_distance(pos1: Position, pos2: Position) -> int:
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def a_star(start: Position, goal: Position, tiles: List[List[TileType]]) -> int | None:
    open_list = []
    heapq.heappush(open_list, (0, start))  # (priority, position)

    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}

    visited = set()

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            return g_score[current]

        visited.add(current)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = Position(current.x + dx, current.y + dy)

            if 0 <= neighbor.x < len(tiles) and 0 <= neighbor.y < len(tiles[0]):
                if tiles[neighbor.x][neighbor.y] == TileType.EMPTY and neighbor not in visited:
                    tentative_g_score = g_score[current] + 1

                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal)
                        heapq.heappush(open_list, (f_score[neighbor], neighbor))

    # If the goal cannot be reached
    return None
