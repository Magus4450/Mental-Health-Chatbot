import os
import re
from typing import Callable, List

import pandas as pd

from src.utils import PathConfig


def get_all_json_data(data_list: List[str] = None) -> pd.DataFrame:
    JSON_BASE_PATH = PathConfig.SCRAPER
    if not data_list:
        all_files = os.listdir()
        data_list = [file for file in all_files if file.endswith("json")]

    file_paths = [f"{JSON_BASE_PATH}/{fn}" for fn in data_list]

    json_df = pd.DataFrame()
    for path in file_paths:
        json_df = pd.concat([json_df, pd.read_json(path)])

    json_df.reset_index(drop=True, inplace=True)

    return json_df


def apply_pipeline_steps(
    json_df: pd.DataFrame, pipeline: Callable[[str, bool], str]
) -> pd.DataFrame:
    json_df["cleaned_text"] = (
        json_df["title"] + " " + json_df["heading"] + " " + json_df["text"]
    )
    json_df["cleaned_text"] = json_df["cleaned_text"].apply(pipeline, args=(True,))
    json_df["text"] = json_df["text"].apply(pipeline, args=(False,))

    return json_df


def remove_escape_chars_and_space(text: str) -> str:
    text = text.replace("\n", " ").replace("\r", "").replace("\t", " ").strip()
    # Remove consecutive spaces
    text = re.sub(" +", " ", text)
    return text


def remove_links(text: str) -> str:
    re_pattern = r"https?:\/\/.*[\r\n]*"
    text = re.sub(re_pattern, "", text, flags=re.MULTILINE)
    return text


def pipeline(text: str, for_embed_text: bool = True) -> str:
    text = remove_escape_chars_and_space(text)
    if for_embed_text:
        text = remove_links(text)
    return text
