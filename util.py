from game_message import Position


def is_in_our_zone(current_team_id: str, position: Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.y][position.x] == current_team_id

def is_not_in_enemies_zone(teamIds: list[str], current_team_id: str, position: Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.y][position.x] not in teamIds or teamZoneGrid[position.y][position.x] == current_team_id

def is_in_enemies_zone(teamIds: list[str], current_team_id: str, position: Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.y][position.x] in teamIds and teamZoneGrid[position.y][position.x] != current_team_id
