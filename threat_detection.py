def find_closest_threats(position: Position, threats: List[Threat], tiles: List[List[TileType]]) -> float:
    min_tick_distance = None
    distances = []
    for threat in threats:
        a_star_distance = a_star(position, threat.position, tiles)
        if a_star_distance is None:
            continue
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