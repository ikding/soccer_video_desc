import logging
from typing import NamedTuple

import yaml

logger = logging.getLogger(__name__)


class Goal(NamedTuple):
    timestamp: str  # video time stamp, not game time stamp (not always available)
    scoring_team: str  # this can only be "H" (home) or "A" (away)
    scoring_player: str
    assist_player: str | None


def soccer_game_description(
    date: str,
    division: str,
    home_team: str,
    away_team: str,
    goals: None | dict[str, None | str | int],
):
    """Generate a description of a soccer game."""
    # Initialize variables for the game description

    team_dict: dict[str, str] = {"H": home_team, "A": away_team}
    team_score: dict[str, int] = {"H": 0, "A": 0}

    description = ""
    # score_h = 0
    # score_a = 0

    # Loop through each goal and add it to the game description
    if goals is not None:
        for goal in goals:
            g = Goal(**goal)  # type: ignore

            team_score[g.scoring_team] += 1

            # Example: 3:27 Surf - Dominic (assist from Ayden): 1-0
            description += (
                f"{g.timestamp} {team_dict[g.scoring_team]} - {g.scoring_player}"
            )
            if g.assist_player is not None:
                description += f" (assist from {g.assist_player})"
            description += f": {team_score['H']}-{team_score['A']}\n"

    # Return the game description as a multiline string
    return description


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open("example.yaml", "r") as stream:
        try:
            game_logs = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logger.error(e)
            raise e

    description = soccer_game_description(
        game_logs["date"],
        game_logs["division"],
        game_logs["home_team"],
        game_logs["away_team"],
        game_logs["goals"],
    )

    print(description)
