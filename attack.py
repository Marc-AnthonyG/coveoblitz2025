from game_message import *
from util import is_not_in_enemies_zone


def attackWith(character_id: str, game_state: TeamGameState) -> list[Action]:
    for item in game_state.items:
        if item.value < 0 and is_not_in_enemies_zone(game_state.teamIds, game_state.currentTeamId, item.position, game_state.teamZoneGrid):
            return [SetSkinAction(character_id, 3),
            MoveToAction(character_id, item.position)]


    