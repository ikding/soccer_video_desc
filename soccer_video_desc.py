import argparse
import logging
import re
from dataclasses import dataclass
from datetime import date, timedelta

import yaml

logger = logging.getLogger(__name__)


@dataclass
class Game:
    """
    A dataclass representing a soccer game.

    Attributes:
        date (date): The date of the game.
        division (str): The division in which the game was played.
        home_team (str): The name of the home team.
        away_team (str): The name of the away team.
        round (str | None): The round of the game, if applicable.
        home_team_abbrev (str | None): The abbreviation of the home team's name, if any.
        away_team_abbrev (str | None): The abbreviation of the away team's name, if any.
    """

    date: date
    division: str
    home_team: str
    away_team: str
    round: str | None = None
    home_team_abbrev: str | None = None
    away_team_abbrev: str | None = None


@dataclass
class Goal:
    """
    A dataclass representing a goal in a soccer game.

    Attributes:
        timestamp (str | int): The video timestamp when the goal was scored, in the
            format 'MM:SS'.
        scoring_team (str): The team that scored the goal. This can only be 'H' (home)
            or 'A' (away).
        scoring_player (str): The player who scored the goal.
        assist_player (str | None): The player who assisted the goal, if any.
        minute (int | None): The game minute when the goal was scored, if known.
    """

    timestamp: str | int
    scoring_team: str
    scoring_player: str
    assist_player: str | None = None
    minute: int | None = None


def split_team_name(team_name: str) -> str:
    """
    Splits the team name at the first occurrence of a pattern that matches two or four
    digits, optionally followed by either "B" or "G".

    Args:
        team_name (str): The team name string to split.

    Returns:
        str: The team name split at the first occurrence of the pattern.
    """
    return re.split(r"\s*\d{2,4}[BG]?\s*", team_name)[0]


def parse_timestamp(timestamp: int | str) -> str:
    """
    Converts a timestamp to a string representation.

    If the timestamp is already a string, it is returned as is. If the timestamp
    is an integer, it is assumed to be in seconds and is converted to a string
    in the format 'MM:SS'.

    Args:
        timestamp (int | str): The timestamp to parse, either as an integer number of
            seconds or as a string.

    Returns:
        str: The timestamp as a string in the format 'MM:SS'.
    """
    if isinstance(timestamp, str):
        return timestamp
    else:
        return ":".join(str(timedelta(seconds=timestamp)).split(":")[1:]).lstrip("0")


def soccer_game_description(game: Game, goals: None | list[Goal]) -> str:
    """
    Generate a description of a soccer game.

    Args:
        date (str): The date of the game.
        division (str): The division in which the game was played.
        round (str | None): The round of the game, if applicable.
        home_team (str): The name of the home team.
        away_team (str): The name of the away team.
        goals (None | dict[str, None | str | int]): A dictionary containing information
            about each goal scored in the game.

    Returns:
        str: A string description of the game, including the final scoreline, the date,
        the division, the round (if applicable), and a description of each goal.
    """
    # Initialize variables for the game description
    team_dict: dict[str, str] = {"H": game.home_team, "A": game.away_team}
    team_short_dict: dict[str, str] = {
        "H": (
            game.home_team_abbrev
            if game.home_team_abbrev
            else split_team_name(game.home_team)
        ),
        "A": (
            game.away_team_abbrev
            if game.away_team_abbrev
            else split_team_name(game.away_team)
        ),
    }
    team_score: dict[str, int] = {"H": 0, "A": 0}
    descriptions = []

    # Loop through each goal and add it to the game description
    if goals is not None:
        for goal in goals:
            description = ""

            team_score[goal.scoring_team] += 1
            if goal.scoring_team == "H":
                scoreline_str = f"[{team_score['H']}]-{team_score['A']}"
            else:
                scoreline_str = f"{team_score['H']}-[{team_score['A']}]"

            # Example: 3:27 Surf - Dominic (assist from Ayden): 1-0
            scoring_player_str = (
                f"#{goal.scoring_player}"
                if isinstance(goal.scoring_player, int)
                else goal.scoring_player
            )
            description += (
                f"{parse_timestamp(goal.timestamp)} "
                f"{team_short_dict['H']} {scoreline_str} {team_short_dict['A']}"
                f" - {scoring_player_str}"
            )
            if goal.assist_player is not None:
                if isinstance(goal.assist_player, int):
                    assist_player_str = f"(assist from #{goal.assist_player})"
                elif goal.assist_player in [
                    "Penalty",
                    "Penalty Kick",
                    "PK",
                    "Free Kick",
                    "Own Goal",
                    "OG",
                ]:
                    assist_player_str = f"({goal.assist_player})"
                else:
                    assist_player_str = f"(assist from {goal.assist_player})"
                description += f" {assist_player_str}"

            if hasattr(goal, "minute") and goal.minute is not None:
                description += f" {goal.minute}'"

            descriptions.append(description)

    final_scoreline = (
        f"{team_dict['H']} {team_score['H']}-{team_score['A']} {team_dict['A']}"
    )
    title_segments = [final_scoreline, game.division, str(game.date)]
    if game.round is not None:
        title_segments.insert(2, game.round)
    title = " | ".join(title_segments) + "\n"
    if len(title) > 100:
        logger.warning(
            f"Title is too long: {len(title)} characters (max 100 characters)"
        )
    subtitle = f"{game.date} {game.division}"
    subtitle += f" ({game.round})\n" if game.round is not None else "\n"

    # Return the game description as a multiline string
    all_strings = [title, subtitle, final_scoreline + "\n"]
    all_strings.extend(descriptions)
    return "\n".join(all_strings)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Get intput yaml file")
    parser.add_argument(
        "yaml_fpath", type=str, help="Yaml file path containing game logs"
    )
    args = parser.parse_args()

    # with open("examples/regular_season.yaml") as f:
    #     game_logs = yaml.safe_load(f)

    with open(args.yaml_fpath, "r") as f:
        try:
            game_logs = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(e)
            raise e

    goals_list = game_logs.pop("goals", None)
    goals = [Goal(**goal) for goal in goals_list]
    game = Game(**game_logs)

    description = soccer_game_description(game, goals)
    logger.info(f"\n{description}\n")
