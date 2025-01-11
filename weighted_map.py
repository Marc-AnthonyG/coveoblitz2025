from collections import deque
from dataclasses import dataclass
from typing import List

from game_message import TileType, TeamGameState, Position


@dataclass
class WeightedMap:
    """Weighted map for calcul."""
    weighted_map: list[list[float]]
    prioritize_drop_point: list[Position]
    prioritize_defence_point: list[Position]

def construct_weighted_map(game_message: TeamGameState) -> WeightedMap:
    """
    Construct a list of list with float point to values tiles. The goal is to have 0 on tiles inaccessible by the player like walls
    and 1 on the tiles where you can go in the most place in 3 turns.
    """
    map: List[List[TileType]] = game_message.map.tiles
    width = len(map)
    height = len(map[0])

    # Initialize the weighted graph with 0.0 for inaccessible tiles
    weighted_map_normilize: List[List[float]] = [[0.0] * height for _ in range(width)]

    # Directions for moving in four directions: left, right, up, down
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # BFS helper function to explore reachable tiles in 3 moves from a given position
    def bfs(start_x: int, start_y: int) -> set[tuple[int, int]]:
        queue = deque([(start_x, start_y, 0)])  # (x, y, distance)
        visited = {(start_x, start_y)}
        accessible_tiles = 0

        while queue:
            x, y, dist = queue.popleft()

            # Stop searching if we've moved more than 10 turns
            if dist >= 10:
                continue

            # Explore adjacent tiles
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited and map[nx][ny] != TileType.WALL:
                    visited.add((nx, ny))
                    accessible_tiles += 1
                    queue.append((nx, ny, dist + 1))

        return visited

    min_reachable_tiles = float('inf')
    max_reachable_tiles = 0
    reachable_map_count = [[0] * height for _ in range(width)]

    for x in range(width):
        for y in range(height):
            if map[x][y] != TileType.WALL:
                reachable_tiles_number = len(bfs(x, y))
                reachable_map_count[x][y] = reachable_tiles_number
                max_reachable_tiles = max(max_reachable_tiles, reachable_tiles_number)
                min_reachable_tiles = min(min_reachable_tiles, reachable_tiles_number)


    for x in range(width):
        for y in range(height):
            if map[x][y] != TileType.WALL:
                weighted_map_normilize[x][y] = (
                        0.22  # Base weight
                        + 0.78 * ((reachable_map_count[x][y] - min_reachable_tiles) / (
                        max_reachable_tiles - min_reachable_tiles))  # Reachable tiles weight
                )


    weighted_zone = []
    for x in range(width):
        for y in range(height):
            if game_message.teamZoneGrid[x][y] == game_message.currentTeamId and weighted_map_normilize[x][y] != 0:
                weighted_zone.append(Position(x, y))

    weighted_zone.sort(key=lambda position: weighted_map_normilize[position.x][position.y])

    defense_list = weighted_zone.copy()
    defense_list.reverse()

    return WeightedMap(weighted_map=weighted_map_normilize, prioritize_drop_point=weighted_zone, prioritize_defence_point=defense_list)
