from typing import List, Dict, Set, Tuple
from collections import defaultdict, deque

from game_message import TileType, Position


def is_valid(pos: Position, maze: List[List[TileType]]) -> bool:
    return (0 <= pos.x < len(maze) and
            0 <= pos.y < len(maze[0]) and
            maze[pos.x][pos.y] == TileType.EMPTY)


def count_neighbors(pos: Position, maze: List[List[TileType]]) -> int:
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    count = 0
    for dx, dy in directions:
        neighbor = Position(pos.x + dx, pos.y + dy)
        if is_valid(neighbor, maze):
            count += 1
    return count


def find_nodes(maze: List[List[TileType]]) -> Set[Position]:
    nodes = set()
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            pos = Position(i, j)
            if maze[i][j] == TileType.EMPTY and count_neighbors(pos, maze) >= 3:
                nodes.add(pos)
    return nodes


def explore_path(start: Position,
                 maze: List[List[TileType]],
                 nodes: Set[Position]) -> List[Tuple[Position, int]]:
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    visited = set([start])
    queue = deque([(start, 0)])  # (position, distance)
    connected_nodes = []

    while queue:
        pos, dist = queue.popleft()
        if pos != start and pos in nodes:
            connected_nodes.append((pos, dist))
            continue

        for dx, dy in directions:
            new_pos = Position(pos.x + dx, pos.y + dy)
            if is_valid(new_pos, maze) and new_pos not in visited:
                visited.add(new_pos)
                queue.append((new_pos, dist + 1))

    return connected_nodes


def maze_to_graph(maze: List[List[TileType]]) -> Dict[Position, List[Tuple[Position, int]]]:
    # Find all nodes (intersections)
    nodes = find_nodes(maze)

    # Create adjacency list
    graph = defaultdict(list)

    # For each node, explore paths to other nodes
    for node in nodes:
        connections = explore_path(node, maze, nodes)
        graph[node].extend(connections)

    return dict(graph)
