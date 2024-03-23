import argparse
import logging
from collections import defaultdict
from pathlib import Path

import pandas as pd  # type: ignore
import yaml
from tqdm.auto import tqdm  # type: ignore
from video_desc_from_yaml import parse_timestamp

logger = logging.getLogger(__name__)


def parse_log_files_to_dataframe(yaml_files: list[Path]) -> pd.DataFrame:
    """
    Converts a list of game logs to a pandas DataFrame.

    Args:
        yaml_files (list[Path]): A list of yaml file paths containing game logs.

    Returns:
        pd.DataFrame: A DataFrame containing the game logs.
    """
    logs_dict = defaultdict(list)

    for yaml_file in tqdm(yaml_files):
        if yaml_file.suffix != ".yaml":
            continue
        with open(yaml_file, "r") as f:
            try:
                game_log = yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error(e)
                raise e

        if "goals" in game_log:
            for goal in game_log["goals"]:
                logs_dict["file_name"].append(yaml_file.stem)
                logs_dict["date"].append(game_log["date"])
                logs_dict["division"].append(game_log["division"])
                logs_dict["round"].append(game_log["round"])
                logs_dict["home_team"].append(game_log["home_team"])
                logs_dict["away_team"].append(game_log["away_team"])
                logs_dict["scoring_team"].append(
                    game_log["home_team"]
                    if goal["scoring_team"] == "H"
                    else game_log["away_team"]
                )
                logs_dict["scoring_player"].append(goal["scoring_player"])
                logs_dict["assist_player"].append(goal.get("assist_player", None))
                logs_dict["timestamp"].append(parse_timestamp(goal["timestamp"]))

    return pd.DataFrame(logs_dict)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Get input yaml file")
    parser.add_argument(
        "yaml_dir", type=str, help="direcotry containing game logs in yaml format"
    )
    args = parser.parse_args()

    yaml_dir_path = Path(args.yaml_dir)

    df = parse_log_files_to_dataframe(sorted(list(yaml_dir_path.iterdir())))
    df.to_csv(yaml_dir_path / "game_logs.csv", index=False)
