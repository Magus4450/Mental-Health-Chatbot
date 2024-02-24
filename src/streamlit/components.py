import random
import time

import streamlit as st
from src.indexer import MilvusCollection
from src.llm import LLM


def write_message(user: str = "assistant", message: str = ""):
    with st.chat_message(user):
        st.write(message)


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


# Streamed response emulator
def response_generator(llm: LLM, mil_col: MilvusCollection, prompt: str):

    contexts = mil_col.search(prompt, limit=5)
    context = [c.text for c in contexts]
    context = "\n".join(context)

    for chunk in llm.invoke_as_gen(context, prompt):
        yield chunk


def streamlit_app(llm: LLM, mil_col: MilvusCollection):
    init_session_state()

    st.title("MHCB")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        write_message(message["role"], message["content"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(llm, mil_col, prompt))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
