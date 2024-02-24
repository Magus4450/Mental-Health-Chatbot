from typing import Any, List

import pandas as pd
from angle_emb import AnglE, Prompts
from loguru import logger


class EmbedModel:
    def __init__(self) -> None:
        self.model = self._load_embedding_model()

    def _load_embedding_model(self) -> Any:
        # Init model
        logger.info("Initializing WhereIsAI/UAE-Large-V1 model for sentence embeddings")
        angle = AnglE.from_pretrained(
            "WhereIsAI/UAE-Large-V1", pooling_strategy="cls"
        ).cuda()
        angle.set_prompt(prompt=Prompts.C)
        return angle

    def embed(self, doc: str) -> List[float]:
        embedding = self.model.encode({"text": doc}).tolist()[0]
        return embedding

    def embed_df(self, data_df: pd.Series) -> List[List[float]]:
        data = data_df.tolist()

        embeds = []
        logger.info(f"Generating embeddings for {len(data)} documents")
        for i, text in enumerate(data):
            embedding = self.embed(text)
            embeds.append(embedding)

            if i > 0 and (i + 1) % 100 == 0:
                logger.info(f"{i+1}/{len(data)}")

        return embeds
