import argparse
from ast import literal_eval
from typing import Dict


def parse_args() -> Dict:

    parser = argparse.ArgumentParser(description="Constrastive arguments")
    parser.add_argument(
        "-c",
        "--create_vdb",
        required=False,
        type=str,
        default="False",
        help="Whether to create vector database or not.",
    )
    parser.add_argument(
        "-n",
        "--new_data",
        required=False,
        type=str,
        default="False",
        help="Flag to see if new data is being added to the database",
    )
    parser.add_argument(
        "-d",
        "--data",
        required=False,
        type=str,
        default="[]",
        help="List of jsons of scraped data",
    )
    parser.add_argument(
        "-de",
        "--debug",
        required=False,
        type=str,
        default="True",
        help="Whether to log in stdout",
    )
    parsed_args = parser.parse_args()
    keys = ["create_vdb", "new_data", "data", "debug"]
    values = [arg for arg in vars(parsed_args).values()]
    kwargs = dict(zip(keys, values))
    print(kwargs)
    kwargs["create_vdb"] = True if kwargs["create_vdb"] == "True" else False
    kwargs["new_data"] = True if kwargs["new_data"] == "True" else False
    kwargs["debug"] = True if kwargs["debug"] == "True" else False
    kwargs["data"] = literal_eval(kwargs["data"])

    return kwargs
