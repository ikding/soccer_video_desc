import pytest
import yaml

from video_desc_from_yaml import (
    Game,
    Goal,
    abbreviate_title,
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
    "input,expected,max_title_length",
    [
        pytest.param(
            "This | is | a | test | title",
            "This|is|a|test|title",
            20,
            id="all-spaces-removed",
        ),
        pytest.param(
            "This | is | a | test | title",
            "This | is | a|test|title",
            24,
            id="some-spaces-removed",
        ),
        pytest.param(
            "This | is | a | test | title",
            "This | is | a | test | title",
            30,
            id="no-spaces-removed",
        ),
    ],
)
def test_abbreviate_title(input, expected, max_title_length):
    assert abbreviate_title(input, max_title_length) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param(
            """
date: 2023-11-04
division: Norcal U12 Premier
home_team: Bay Area Surf 13B Pre-MLS
away_team: Palo Alto SC 12B Gold
goals:
  - timestamp: 3:27
    scoring_team: H
    scoring_player: Dominic
    assist_player: Ayden
    minute: 4
  - timestamp: 4:47
    scoring_team: H
    scoring_player: Galvan
    assist_player: PK
    minute: 5
  - timestamp: 10:03
    scoring_team: A
    scoring_player: 27
    assist_player: 70
    minute: 11
  - timestamp: 11:02
    scoring_team: A
    scoring_player: 90
    assist_player: FK
    minute: 12
  - timestamp: 11:32
    scoring_team: H
    scoring_player: null
    assist_player: OG
    minute: 13
            """,
            """
Bay Area Surf 13B Pre-MLS 3-2 Palo Alto SC 12B Gold | Norcal U12 Premier | 2023-11-04

2023-11-04 Norcal U12 Premier

Bay Area Surf 13B Pre-MLS 3-2 Palo Alto SC 12B Gold

3:27 Bay Area Surf [1]-0 Palo Alto SC - Dominic (assist from Ayden) 4'
4:47 Bay Area Surf [2]-0 Palo Alto SC - Galvan (penalty kick) 5'
10:03 Bay Area Surf 2-[1] Palo Alto SC - #27 (assist from #70) 11'
11:02 Bay Area Surf 2-[2] Palo Alto SC - #90 (free kick) 12'
11:32 Bay Area Surf [3]-2 Palo Alto SC - None (own goal) 13'""",
            id="regular-season",
        ),
        pytest.param(
            """
date: 2023-10-29
division: LV Mayor's Cup U11 1st Div
round: Final
home_team: Bay Area Surf 13B Pre-MLS
home_team_abbrev: Surf
away_team: CV Futbol Academy 13B I
away_team_abbrev: CVFA
goals:
  - timestamp: 3:23
    scoring_team: H
    scoring_player: Eli
    assist_player: FK
    minute: 13
  - timestamp: 4:26
    scoring_team: H
    scoring_player: Galvan
    assist_player: Alexander
    minute: 19
  - timestamp: 7:58
    scoring_team: H
    scoring_player: Dominic
    assist_player: Galvan
    minute: 29
  - timestamp: 9:04
    scoring_team: H
    scoring_player: Dominic
    assist_player: Alexander
    minute: 60+2
            """,
            """
Bay Area Surf 13B Pre-MLS 4-0 CV Futbol Academy 13B I | LV Mayor's Cup U11 1st Div|Final|2023-10-29

2023-10-29 LV Mayor's Cup U11 1st Div (Final)

Bay Area Surf 13B Pre-MLS 4-0 CV Futbol Academy 13B I

3:23 Surf [1]-0 CVFA - Eli (free kick) 13'
4:26 Surf [2]-0 CVFA - Galvan (assist from Alexander) 19'
7:58 Surf [3]-0 CVFA - Dominic (assist from Galvan) 29'
9:04 Surf [4]-0 CVFA - Dominic (assist from Alexander) 60+2'""",
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
