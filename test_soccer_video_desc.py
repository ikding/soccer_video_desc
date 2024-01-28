from pathlib import Path

import yaml

from soccer_video_desc import (
    Game,
    Goal,
    parse_timestamp,
    soccer_game_description,
    split_team_name,
)


def test_split_team_name():
    assert split_team_name("Bay Area Surf 13B Pre-MLS") == "Bay Area Surf"
    assert split_team_name("Team Name 1234G Extra Info") == "Team Name"
    assert split_team_name("No Numbers Or Letters Here") == "No Numbers Or Letters Here"


def test_parse_timestamp():
    assert parse_timestamp(90) == "1:30"
    assert parse_timestamp("00:45") == "00:45"


def test_soccer_game_description_regular_season():
    with open(
        Path(__file__).parent.resolve() / "examples" / "regular_season.yaml", "r"
    ) as f:
        game_logs = yaml.safe_load(f)

    goals_list = game_logs.pop("goals", None)
    goals = [Goal(**goal) for goal in goals_list]
    game = Game(**game_logs)

    description = soccer_game_description(game, goals)
    assert "\n" + description + "\n" == """
Bay Area Surf 13B Pre-MLS 6-2 Palo Alto SC 12B Gold | Norcal U12 Premier | 2023-11-04

2023-11-04 Norcal U12 Premier

Bay Area Surf 13B Pre-MLS 6-2 Palo Alto SC 12B Gold

3:27 Bay Area Surf [1]-0 Palo Alto SC - Dominic (assist from Ayden)
4:47 Bay Area Surf [2]-0 Palo Alto SC - Galvan
7:58 Bay Area Surf [3]-0 Palo Alto SC - Dominic (assist from Joshua)
8:33 Bay Area Surf [4]-0 Palo Alto SC - Dominic (assist from Ryan)
9:00 Bay Area Surf [5]-0 Palo Alto SC - Cameron (assist from Owen)
10:03 Bay Area Surf 5-[1] Palo Alto SC - #27 (assist from #70)
11:02 Bay Area Surf 5-[2] Palo Alto SC - #90 (assist from #6)
11:32 Bay Area Surf [6]-2 Palo Alto SC - Dominic
"""


def test_soccer_game_description_tournament():
    with open(
        Path(__file__).parent.resolve() / "examples" / "tournament.yaml", "r"
    ) as f:
        game_logs = yaml.safe_load(f)

    goals_list = game_logs.pop("goals", None)
    goals = [Goal(**goal) for goal in goals_list]
    game = Game(**game_logs)

    description = soccer_game_description(game, goals)
    assert "\n" + description + "\n" == """
Bay Area Surf 13B Pre-MLS 4-0 CVFA 13B I | LV Mayor's Cup U11 1st Div | Final | 2023-10-29

2023-10-29 LV Mayor's Cup U11 1st Div (Final)

Bay Area Surf 13B Pre-MLS 4-0 CVFA 13B I

3:23 Bay Area Surf [1]-0 CVFA - Eli (Free Kick)
4:26 Bay Area Surf [2]-0 CVFA - Galvan (assist from Alexander)
7:58 Bay Area Surf [3]-0 CVFA - Dominic (assist from Galvan)
9:04 Bay Area Surf [4]-0 CVFA - Dominic (assist from Alexander)
"""
