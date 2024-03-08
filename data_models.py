from dataclasses import dataclass
from datetime import date


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
