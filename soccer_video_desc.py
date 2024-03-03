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


scoring_abbrev: dict[str, str] = {
    "PK": "penalty kick",
    "FK": "free kick",
    "OG": "own goal",
    "CK": "corner kick",
}


def split_team_name(team_name: str) -> str:
    """
    Splits the team name at the first occurrence of a pattern that matches two or four
    digits, optionally lead by or followed by either "B" or "G".

    Args:
        team_name (str): The team name string to split.

    Returns:
        str: The team name split at the first occurrence of the pattern.
    """
    return re.split(r"\s*[BG]?\d{2,4}[BG]?\s*", team_name)[0]


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


def abbreviate_title(title: str, max_title_length: int = 100) -> str:
    """
    Abbreviates a title by removing spaces around pipe characters, from right to left.

    Args:
        title (str): The title to abbreviate.

    Returns:
        str: The abbreviated title.
        max_title_length (int, optional): The maximum length of the title. Defaults to
            100.
    """
    segments = title.split("|")
    for i in range(len(segments) - 1, 0, -1):
        if len(title) <= max_title_length:
            break
        segments[i] = segments[i].strip()
        segments[i - 1] = segments[i - 1].rstrip()
        title = "|".join(segments)

    return title


def soccer_game_description(
    game: Game, goals: None | list[Goal], max_title_length: int = 100
) -> str:
    """
    Generates a description for a soccer game.

    The description includes the final scoreline, the division, the date, and a list of
    goals. Each goal is represented by a string that includes the timestamp, the scoring
    team, the scoreline after the goal, the player who scored the goal, and optionally
    the player who assisted the goal and the game minute of the goal.

    Args:
        game (Game): The game for which to generate a description.
        goals (None | list[Goal]): A list of goals scored during the game.
        max_title_length (int, optional): The maximum length of the title. Defaults to
            100.

    Returns:
        str: A string containing the game description.
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
                elif goal.assist_player.upper() in scoring_abbrev.keys():
                    assist_player_str = f"({scoring_abbrev[goal.assist_player]})"
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

    if len(title) > max_title_length + 1:  # 100 characters + 1 newline
        logger.warning(
            f"Title is too long: {len(title)} characters "
            f"(max {max_title_length} characters)"
        )

        new_title = abbreviate_title(title) + "\n"
        if len(new_title) > max_title_length + 1:
            pass
        else:
            logger.info(
                f"Abbreviating title to fit within {max_title_length} characters. "
                f"New length: {len(new_title) - 1}"  # subtract 1 for newline
            )
            title = new_title

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
    title_length = len(description.split("\n")[0])
    logger.info(f"title length: {title_length} characters\n\n{description}\n")
