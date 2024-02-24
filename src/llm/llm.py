from typing import Generator

from langchain.llms import Ollama
from loguru import logger


class LLM:

    def __init__(self) -> None:
        self.model = self._init_model()

    def _init_model(self):
        logger.info("Loading mistral model")
        try:
            self.model = Ollama(model="mistral")
            logger.success("Successfully loaded the model")
        except Exception as e:
            logger.error("Couldn't load mistral model")

    def _build_prompt(self, context: str, question: str) -> str:
        return f"""You are a chatbot that answer mental health related questions asked by the user. Use the following pieces of context to answer the questions at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Do not elaborate the answer, make it short. Do not get questions from context.\nContext: {context}\nQuestion: {question}\nAnswer: 
        """

    def invoke(self, context: str, question: str) -> str:
        prompt = self._build_prompt(context, question)

        logger.info(f"Prompting the LLM with query:\n{prompt}")

        try:
            out = llm.invoke(prompt)
        except Exception as e:
            out = ""
            logger.error("Error querying the LLM\n{e}")
        return out

    def invoke_as_gen(self, context: str, question: str) -> Generator:
        prompt = self._build_prompt(context, question)

        logger.info(f"Prompting the LLM with query:\n{prompt}")

        try:
            for chunk in llm.stream(prompt):
                yield chunk

        except Exception as e:
            out = ""
            logger.error("Error querying the LLM\n{e}")


llm = Ollama(model="mistral")
