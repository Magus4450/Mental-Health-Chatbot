from typing import Any, Dict, List, Tuple

import pandas as pd
from loguru import logger
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    has_collection,
    utility,
)

from src.indexer.embed import EmbedModel


class MilvusCollection:

    def __init__(
        self,
        alias: str,
        host: str,
        port: str,
        collection_name: str,
        embedding_dim: int = 1024,
        embedding_model: EmbedModel = None,
        index_param_kwargs: Dict = None,
        delete_old_collection: bool = False,
    ):

        # Make connection
        self._make_connection(alias, host, port)
        if delete_old_collection:
            MilvusCollection.delete_collection(collection_name)

        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.embedding_model = embedding_model
        self.index_params = self._get_index_params(index_param_kwargs)

        self.schema = self._get_schema()
        self.collection = self._create_or_get_collection()

    def _make_connection(self, alias: str, host: str, port: str) -> None:
        try:
            connections.connect(alias="default", host="localhost", port="19530")
            logger.success(
                f"Successfully connected to alias:{alias} host:{host} port:{port}"
            )
        except Exception as e:
            logger.error(f"Couldnt connect.\n{e}")

    def _get_schema(self) -> CollectionSchema:
        id = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
        title = FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=100)
        heading = FieldSchema(name="heading", dtype=DataType.VARCHAR, max_length=200)
        text = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=20000)
        embeddings = FieldSchema(
            name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim
        )

        schema = CollectionSchema(
            fields=[id, title, heading, text, embeddings],
            description="Mental Heath Data",
            enable_dynamic_field=True,
        )

        return schema

    def _create_or_get_collection(self) -> Collection:

        if has_collection(self.collection_name):
            logger.info(f"Collection {self.collection_name} already exixts")
            collection = Collection(name=self.collection_name)
        else:
            logger.info(
                f"Creating collection: {self.collection_name} with schema: {self.schema}"
            )

            try:
                collection = Collection(
                    name=self.collection_name,
                    schema=self.schema,
                    using="default",
                    shard_num=2,
                )
                logger.success("Collection successfully created collection")
            except Exception as e:
                logger.error(f"Couldn't create collection.\n{e}")

        return collection

    @staticmethod
    def delete_collection(collection_name: str) -> None:

        logger.info(f"Deleting collection {collection_name}")
        try:
            utility.drop_collection(collection_name)
            logger.success("Collection deleted successfully")
        except Exception as e:
            logger.error("Couldn't delete collection\n{e}")

    def create_entities_to_insert(self, data_df: pd.DataFrame) -> List[List]:
        data = [
            data_df["title"].tolist(),
            data_df["heading"].tolist(),
            data_df["text"].tolist(),
            self.embedding_model.embed_df(data_df["cleaned_text"]),
        ]
        return data

    def insert_entities_from_df(self, data_df: pd.DataFrame) -> None:
        entities = self.create_entities_to_insert(data_df)
        self.insert_entities(entities)

    def insert_entities(self, entities: List[List]) -> None:
        n_entities = len(entities[0])
        logger.info(f"Inserting {n_entities} into collection {self.collection_name}")
        try:
            self.collection.insert(entities)
            logger.success(f"Successfully inserted {n_entities} entities")
        except Exception as e:
            logger.error(f"Couldn't insert entities\n{e}")

    def _get_index_params(self, index_param_kwargs) -> Dict[str, Any]:

        if index_param_kwargs:
            return index_param_kwargs
        else:
            return {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024},
            }

    def build_index(self) -> None:
        logger.info(f"Creating vector index with params: {self.index_params}")
        try:
            self.collection.create_index(
                field_name="embeddings", index_params=self.index_params
            )
            logger.success("Successfully created vector index")
        except Exception as e:
            logger.error(f"Couldn't create vector index\n{e}")

    def _get_search_params(self) -> Dict[str, Any]:
        return {
            "metric_type": self.index_params["metric_type"],
            "offset": 0,
            "ignore_growing": False,
            "params": {"nprobe": 10},
        }

    def search(
        self,
        doc: str,
        output_fields: List[str] = ["title", "heading", "text"],
        limit: int = 10,
        expr: str = None,
    ):
        search_params = self._get_search_params()
        self.collection.load()
        logger.info(f"Performing search for\ndocument:{doc}\n")
        embedding = self.embedding_model.embed(doc)
        try:
            results = self.collection.search(
                data=[embedding],
                anns_field="embeddings",
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=output_fields,
            )
            self.collection.release()

            logger.info(f"Successfully retrieved {limit} documents\n{results}")
            return results[0]
        except Exception as e:
            logger.error(f"Couldn't perform search\n{e}")

    def get_count(self) -> int:
        self.collection.load()
        logger.info("Performing count query")
        try:
            results = self.collection.query(
                expr="",
                output_fields=["count(*)"],
            )
            print(results)
            results = results[0]["count(*)"]
            logger.success(f"Output: {results}")
            self.collection.release()
            return results
        except Exception as e:
            logger.error(f"Couldn't perform count query\n{e}")
            return -1
