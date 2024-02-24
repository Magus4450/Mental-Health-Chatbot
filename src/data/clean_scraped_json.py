import re

import pandas as pd

from src.utils import PathConfig


def get_all_json_data() -> pd.DataFrame:
    JSON_BASE_PATH = PathConfig.SCRAPER
    file_names = ["nami.json", "nimh.json"]
    file_paths = [f"{JSON_BASE_PATH}/{fn}" for fn in file_names]

    json_df = pd.DataFrame()
    for path in file_paths:
        json_df = pd.concat([json_df, pd.read_json(path)])

    json_df.reset_index(drop=True, inplace=True)

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
