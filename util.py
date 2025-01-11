from game_message import Position


def is_in_our_zone(current_team_id: str, position: Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.x][position.y] == current_team_id

def is_not_in_enemies_zone(teamIds: list[str], current_team_id: str, position: Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.x][position.y] not in teamIds or teamZoneGrid[position.x][position.y] == current_team_id

def is_in_enemies_zone(teamIds: list[str], current_team_id: str, position: Position,  teamZoneGrid: list[list[str]]) -> bool:
    return teamZoneGrid[position.x][position.y] in teamIds and teamZoneGrid[position.x][position.y] != current_team_id
