from pathlib import Path

import pytest
import yaml

from soccer_video_desc import (
    Game,
    Goal,
    parse_timestamp,
    soccer_game_description,
    split_team_name,
)


@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param(
            "Bay Area Surf 13B Pre-MLS", "Bay Area Surf", id="two-digits-with-gender"
        ),
        pytest.param(
            "Bay Area Surf 2013 Black", "Bay Area Surf", id="four-digits-without-gender"
        ),
        pytest.param("Bay Area Surf", "Bay Area Surf", id="no-extra-info"),
    ],
)
def test_split_team_name(input, expected):
    assert split_team_name(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param(90, "1:30", id="int-seconds"),
        pytest.param("00:45", "00:45", id="str-minutes-seconds"),
    ],
)
def test_parse_timestamp(input, expected):
    assert parse_timestamp(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param(
            """
date: 2023-11-04
division: Norcal U12 Premier
round: null
home_team: Bay Area Surf 13B Pre-MLS
away_team: Palo Alto SC 12B Gold
goals:
  - timestamp: 3:27
    scoring_team: H
    scoring_player: Dominic
    assist_player: Ayden
  - timestamp: 4:47
    scoring_team: H
    scoring_player: Galvan
    assist_player: null
  - timestamp: 7:58
    scoring_team: H
    scoring_player: Dominic
    assist_player: Joshua
  - timestamp: 8:33
    scoring_team: H
    scoring_player: Dominic
    assist_player: Ryan
  - timestamp: 9:00
    scoring_team: H
    scoring_player: Cameron
    assist_player: Owen
  - timestamp: 10:03
    scoring_team: A
    scoring_player: 27
    assist_player: 70
  - timestamp: 11:02
    scoring_team: A
    scoring_player: 90
    assist_player: 6
  - timestamp: 11:32
    scoring_team: H
    scoring_player: Dominic
    assist_player: null
            """,
            """
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
11:32 Bay Area Surf [6]-2 Palo Alto SC - Dominic""",
            id="regular season",
        ),
        pytest.param(
            """
date: 2023-10-29
division: LV Mayor's Cup U11 1st Div
round: Final
home_team: Bay Area Surf 13B Pre-MLS
away_team: CVFA 13B I
goals:
  - timestamp: 3:23
    scoring_team: H
    scoring_player: Eli
    assist_player: Free Kick
  - timestamp: 4:26
    scoring_team: H
    scoring_player: Galvan
    assist_player: Alexander
  - timestamp: 7:58
    scoring_team: H
    scoring_player: Dominic
    assist_player: Galvan
  - timestamp: 9:04
    scoring_team: H
    scoring_player: Dominic
    assist_player: Alexander
            """,
            """
Bay Area Surf 13B Pre-MLS 4-0 CVFA 13B I | LV Mayor's Cup U11 1st Div | Final | 2023-10-29

2023-10-29 LV Mayor's Cup U11 1st Div (Final)

Bay Area Surf 13B Pre-MLS 4-0 CVFA 13B I

3:23 Bay Area Surf [1]-0 CVFA - Eli (Free Kick)
4:26 Bay Area Surf [2]-0 CVFA - Galvan (assist from Alexander)
7:58 Bay Area Surf [3]-0 CVFA - Dominic (assist from Galvan)
9:04 Bay Area Surf [4]-0 CVFA - Dominic (assist from Alexander)""",
            id="tournament",
        ),
    ],
)
def test_soccer_game_description(input, expected):
    game_logs = yaml.safe_load(input)
    goals_list = game_logs.pop("goals", None)
    goals = [Goal(**goal) for goal in goals_list]
    game = Game(**game_logs)

    description = soccer_game_description(game, goals)
    assert description == expected.strip("\n")
