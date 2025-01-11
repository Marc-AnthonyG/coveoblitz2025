from collections import deque
from typing import List

from game_message import TileType, Threat, Position


def construct_weighted_map(map: List[List[TileType]], spawn_position: Position) -> list[list[float]]:
    """
    Construct a list of list with float point to values tiles. The goal is to have 0 on tiles inaccessible by the player like walls
    and 1 on the tiles where you can go in the most place in 3 turns.
    """
    width = len(map)
    height = len(map[0])

    # Initialize the weighted graph with 0.0 for inaccessible tiles
    weighted_map_normilize: List[List[float]] = [[0.0] * height for _ in range(width)]

    # Directions for moving in four directions: left, right, up, down
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # BFS helper function to explore reachable tiles in 3 moves from a given position
    def bfs(start_x: int, start_y: int, dont_stop: bool = False) -> set[tuple[int, int]]:
        queue = deque([(start_x, start_y, 0)])  # (x, y, distance)
        visited = {(start_x, start_y)}
        accessible_tiles = 0

        while queue:
            x, y, dist = queue.popleft()

            # Stop searching if we've moved more than 3 turns
            if dist >= 10 and not dont_stop:
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

    visitable_tiles = bfs(spawn_position.x, spawn_position.y, True)
    for x, y in visitable_tiles:
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

    return weighted_map_normilize
