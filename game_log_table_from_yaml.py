import argparse
import logging
from collections import defaultdict
from pathlib import Path

import pandas as pd
import yaml
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)


def load_logs_to_dataframe(logs: list[dict]) -> pd.DataFrame:
    """
    Converts a list of game logs to a pandas DataFrame.

    Args:
        logs (list[dict]): A list of game logs, where each log is a dictionary.

    Returns:
        pd.DataFrame: A DataFrame containing the game logs.
    """
    logs_dict = defaultdict(list)

    for log in tqdm(logs, desc="games"):
        if "goals" in log:
            for goal in log["goals"]:
                logs_dict["date"].append(log["date"])
                logs_dict["division"].append(log["division"])
                logs_dict["round"].append(log["round"])
                logs_dict["home_team"].append(log["home_team"])
                logs_dict["away_team"].append(log["away_team"])
                logs_dict["scoring_team"].append(goal["scoring_team"])
                logs_dict["scoring_player"].append(goal["scoring_player"])
                logs_dict["assist_player"].append(goal.get("assist_player", None))
                logs_dict["minute"].append(goal.get("minute", None))

    return pd.DataFrame(logs_dict)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Get input yaml file")
    parser.add_argument(
        "yaml_dir", type=str, help="direcotry containing game logs in yaml format"
    )
    args = parser.parse_args()

    yaml_dir_path = Path(args.yaml_dir)

    game_logs_list = []
    for yaml_file in yaml_dir_path.iterdir():
        if yaml_file.suffix != ".yaml":
            continue
        with open(yaml_file, "r") as f:
            try:
                game_logs = yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error(e)
                raise e

            game_logs_list.append(game_logs)

    df = load_logs_to_dataframe(game_logs_list)

    print(df)
