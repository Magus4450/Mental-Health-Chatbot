import os

from loguru import logger

import streamlit as st
from src.data import apply_pipeline_steps, get_all_json_data
from src.data import pipeline as data_clean_pipeline
from src.indexer import EmbedModel, MilvusCollection
from src.llm import LLM
from src.streamlit import streamlit_app
from src.utils import PathConfig, TimeConfig, parse_args


def main() -> None:

    kwargs = parse_args()
    logger.info(f"Kwargs:\n{kwargs}")

    date_time = TimeConfig.DATETIME
    log_base_path = PathConfig.LOG

    # Remove logging in stdout
    if not kwargs["debug"]:
        logger.remove()

    log_path = os.path.join(log_base_path, f"{date_time}.log")
    logger.add(log_path)

    llm, mil_con = get_streamlit_components(kwargs["create_vdb"])

    if kwargs["create_vdb"] or kwargs["new_data"]:
        logger.info("Collecting scraped data from json")
        json_df = get_all_json_data(None if kwargs["create_vdb"] else kwargs["data"])
        logger.info("Cleaning the scraped text data")
        json_df = apply_pipeline_steps(json_df, data_clean_pipeline)

        # Insert data
        mil_con.insert_entities_from_df(json_df)

        # Create vector index
        mil_con.build_index()

    streamlit_app(llm=llm, mil_col=mil_con)


@st.cache_resource
def get_streamlit_components(delete_old_collection: bool):
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
        delete_old_collection=delete_old_collection,
    )
    llm = LLM()
    return llm, mil_con


if __name__ == "__main__":
    main()
