import os

from loguru import logger

import streamlit as st
from src.data import get_all_json_data
from src.data import pipeline as data_clean_pipeline
from src.indexer import EmbedModel, MilvusCollection
from src.llm import LLM
from src.streamlit import streamlit_app
from src.utils import PathConfig, TimeConfig


def main() -> None:
    date_time = TimeConfig.DATETIME
    log_base_path = PathConfig.LOG

    # Remove logging in stdout
    # logger.remove()

    log_path = os.path.join(log_base_path, f"{date_time}.log")
    logger.add(log_path)

    logger.info("Collecting scraped data from json")
    json_df = get_all_json_data()

    logger.info("Cleaning the scraped text data")
    json_df["cleaned_text"] = (
        json_df["title"] + " " + json_df["heading"] + " " + json_df["text"]
    )
    json_df["cleaned_text"] = json_df["cleaned_text"].apply(
        data_clean_pipeline, args=(True,)
    )
    json_df["text"] = json_df["text"].apply(data_clean_pipeline, args=(False,))

    embed_model = EmbedModel()

    mil_con = MilvusCollection(
        alias="default",
        host="localhost",
        port="19530",
        collection_name="mental_health_data",
        embedding_dim=1024,
        embedding_model=embed_model,
        index_param_kwargs={
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024},
        },
        # delete_old_collection=True,
    )

    # Insert data
    # mil_con.insert_entities_from_df(json_df)

    # # Create vector index
    # mil_con.build_index()

    # print(mil_con.get_count())

    # test_doc = "What are the symptoms of depression?"

    # print(mil_con.search(test_doc))

    llm = LLM()

    test_question = "What are the symptoms of depression?"

    contexts = mil_con.search(test_question, limit=2)
    print(contexts)

    context = [c.text for c in contexts]
    context = "\n".join(context)

    ans = llm.invoke(context, test_question)

    print(test_question)
    print(ans)


@st.cache_resource
def get_streamlit_components():
    embed_model = EmbedModel()

    mil_con = MilvusCollection(
        alias="default",
        host="localhost",
        port="19530",
        collection_name="mental_health_data",
        embedding_dim=1024,
        embedding_model=embed_model,
        index_param_kwargs={
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024},
        },
    )
    llm = LLM()
    return llm, mil_con


def run_streamlit():
    llm, mil_con = get_streamlit_components()
    streamlit_app(llm=llm, mil_col=mil_con)


if __name__ == "__main__":
    run_streamlit()
