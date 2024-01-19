import logging
import re
from typing import NamedTuple

import yaml

logger = logging.getLogger(__name__)


class Goal(NamedTuple):
    timestamp: str  # video time stamp (MM:SS)
    scoring_team: str  # this can only be "H" (home) or "A" (away)
    scoring_player: str
    assist_player: str | None


def split_team_name(team_name: str):
    return re.split(r"\s*\d{2}[BG]\s*", team_name)[0]


def soccer_game_description(
    date: str,
    division: str,
    round: str | None,
    home_team: str,
    away_team: str,
    goals: None | dict[str, None | str | int],
):
    """Generate a description of a soccer game."""
    # Initialize variables for the game description
    team_dict: dict[str, str] = {"H": home_team, "A": away_team}
    team_short_dict: dict[str, str] = {
        "H": split_team_name(home_team),
        "A": split_team_name(away_team),
    }
    team_score: dict[str, int] = {"H": 0, "A": 0}
    descriptions = []

    # Loop through each goal and add it to the game description
    if goals is not None:
        for goal in goals:
            description = ""
            g = Goal(**goal)  # type: ignore

            team_score[g.scoring_team] += 1
            if g.scoring_team == "H":
                scoreline_str = f"[{team_score['H']}]-{team_score['A']}"
            else:
                scoreline_str = f"{team_score['H']}-[{team_score['A']}]"

            # Example: 3:27 Surf - Dominic (assist from Ayden): 1-0
            scoring_player_str = (
                f"#{g.scoring_player}"
                if isinstance(g.scoring_player, int)
                else g.scoring_player
            )
            description += (
                f"{g.timestamp} "
                f"{team_short_dict['H']} {scoreline_str} {team_short_dict['A']}"
                f" - {scoring_player_str}"
            )
            if g.assist_player is not None:
                if isinstance(g.assist_player, int):
                    assist_player_str = f"(assist from #{g.assist_player})"
                elif g.assist_player in [
                    "Penalty",
                    "Penalty Kick",
                    "PK",
                    "Free Kick",
                    "Own Goal",
                    "OG",
                ]:
                    assist_player_str = f"({g.assist_player})"
                else:
                    assist_player_str = f"(assist from {g.assist_player})"
                description += f" {assist_player_str}"

            descriptions.append(description)

    final_scoreline = (
        f"{team_dict['H']} {team_score['H']} - {team_score['A']} {team_dict['A']}"
    )
    title_segments = [final_scoreline, division, date]
    if round is not None:
        title_segments.insert(2, round)
    title = " | ".join(title_segments) + "\n"
    if len(title) > 100:
        logger.warning(
            f"Title is too long: {len(title)} characters (max 100 characters)"
        )
    subtitle = f"{date} {division}"
    subtitle += f" ({round})\n" if round is not None else "\n"

    # Return the game description as a multiline string
    all_strings = [title, subtitle, final_scoreline + "\n"]
    all_strings.extend(descriptions)
    return "\n".join(all_strings)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open("example.yaml", "r") as stream:
        try:
            game_logs = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logger.error(e)
            raise e

    description = soccer_game_description(**game_logs)
    print(description)
