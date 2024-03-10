import logging
import yaml
import re
from datetime import date
from difflib import get_close_matches
from dataclasses import asdict

from data_models import Game, Goal

logger = logging.getLogger(__name__)


def split_multiline_string(string: str) -> list[str]:
    """
    Splits a multiline string into a list of strings.

    Args:
        string (str): The multiline string to split.

    Returns:
        list[str]: A list of strings, where each string is a line from the original
        string. Empty lines are excluded and leading and trailing whitespace is removed
        from each line.
    """
    return [s.strip() for s in re.split(r"\n", string) if len(s.strip()) > 0]


def parse_title(string: str) -> tuple[date, str]:
    """
    Parses a title string into a date and a division.

    Args:
        string (str): The title string to parse. It should start with a date in ISO
            format (YYYY-MM-DD), followed by a space, followed by the division.

    Returns:
        tuple[date, str]: A tuple containing the date and the division.
    """
    try:
        date_str, division = string.split(" ", 1)
        return date.fromisoformat(date_str), division
    except ValueError:
        raise ValueError(f"Title string {string} must contain a date and a division.")


def parse_team(scoreline: str) -> tuple:
    """
    Splits a scoreline string into a tuple of team names.

    Args:
        scoreline (str): The scoreline string to split.

    Returns:
        tuple: A tuple containing the names of the two teams.
    """
    teams = re.split(r"\s\d{1,2}\s?:\s?\d{1,2}\s", scoreline)
    return (teams[0], teams[1])


def parse_goal(string: str, home_team: str, away_team: str) -> Goal:
    """
    Parses a string representing a goal scored in a soccer game.

    The string should be in the format "MM:SS Team - Player (assist from Player):
    Scoreline".

    Args:
        string (str): The string representing the goal.
        home_team (str): The name of the home team.
        away_team (str): The name of the away team.

    Returns:
        Goal: A Goal object representing the goal.
    """
    timestamp, rest = string.split(" ", 1)
    scoring_team, rest = rest.split(" - ", 1)
    if "assist from" in rest:
        scoring_player, rest = rest.split(" (assist from ", 1)
        # assist_player, rest = rest.split(r")\s?:\s?", 1)
        assist_player, rest = re.split(r"\)\s?:", rest)
    else:
        scoring_player = rest.split(":")[0].strip()
        assist_player = None
    minute = None

    if " (assist from " in rest:
        assist_player, rest = rest.split(" (assist from ", 1)
        assist_player = assist_player.strip()
        assist_player = assist_player.rstrip(")")

    scoring_team = get_close_matches(
        scoring_team, [home_team, away_team], n=1, cutoff=0.25
    )[0]

    if scoring_team == home_team:
        scoring_team = "H"
    elif scoring_team == away_team:
        scoring_team = "A"
    else:
        raise ValueError(
            f"{scoring_team=} is not one of the game teams: {home_team=}, {away_team=}."
        )

    if scoring_player is not None and scoring_player.startswith("#"):
        scoring_player = int(scoring_player[1:])
    if assist_player is not None and assist_player.startswith("#"):
        assist_player = int(assist_player[1:])

    return Goal(
        timestamp=timestamp,
        scoring_team=scoring_team,
        scoring_player=scoring_player,
        assist_player=assist_player,
        minute=minute,
    )


def parse_all_fields(multiline_string: str) -> tuple[Game, list[Goal]]:
    """
    Parses a multiline string into a Game object and a list of Goal objects.

    Args:
        multiline_string (str): The multiline string to parse. The first line should
            contain the game date and division, the second line should contain the home
            and away teams, and the remaining lines should contain the goals.

    Returns:
        tuple[Game, list[Goal]]: A tuple containing a Game object and a list of Goal
        objects.

    The Game object is created from the date, division, home team, and away team.
    Each Goal object is created from a line that starts with a timestamp.
    """
    strings = split_multiline_string(multiline_string)
    game_date, division = parse_title(strings[0])
    home_team, away_team = parse_team(strings[1])

    game = Game(
        date=game_date, division=division, home_team=home_team, away_team=away_team
    )

    goals = []
    for string in strings[2:]:
        if re.match(r"^\d{1,2}:\d{2}", string):
            goal = parse_goal(string, home_team, away_team)
            goals.append(goal)

    return game, goals


def convert_to_yaml(game: Game, goals: list[Goal] | None) -> str:
    """
    Converts a Game object and a list of Goal objects to a YAML string.

    Args:
        game (Game): The Game object to convert.
        goals (list[Goal] | None): The list of Goal objects to convert. If None, no
            goals are added to the game.

    Returns:
        str: A YAML string representing the game and the goals.

    The Game object is converted to a dictionary using the asdict function from the
    dataclasses module. Each Goal object is also converted to a dictionary using the
    asdict function. The dictionaries are then converted to a YAML string using the dump
    function from the PyYAML module.
    """
    game_dict = asdict(game)
    if goals is not None:
        goals_list = [asdict(goal) for goal in goals]
        game_dict["goals"] = goals_list
    return yaml.dump(game_dict, sort_keys=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    multiline_string = """
2022-09-10 Norcal U10B Region 1/2 Gold South

Bay Area Surf 2 : 4 ECFC

4:11 ECFC - #8: 0-1
5:06 ECFC - #8 (assist from #20): 0-2
6:45 ECFC - #3: 0-3
9:42 ECFC - #6 (assist from #11) : 0-4
10:01 Surf - Luke: 1-4
10:31 Surf - Jamie (assist from Alex): 2-4

Norcal U10B Region 1/2 Gold South (2022 fall league) - Event Page: https://system.gotsport.com/org_event/events/15482/schedules?group=90450

2022/23 (2013B) Norcal U10 Playlist: https://youtube.com/playlist?list=PLo96kgYq9NqugI0qLezxyQB0Z891dNvBJ
"""

    game, goals = parse_all_fields(multiline_string)
    yaml_fname = f"{game.date} {game.home_team} vs {game.away_team}.yaml"
    yaml_string = convert_to_yaml(game, goals)

    logger.info(f"\n\n{yaml_fname}\n\n{yaml_string}")

    logger.info(f"Writing YAML to logs/{yaml_fname}")
    with open(f"logs/{yaml_fname}", "w") as f:
        f.write(yaml_string)
