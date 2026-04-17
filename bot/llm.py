from openai import api_key, embeddings
import streamlit as st

# Create the LLM
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_key = st.session_state.openai_api_key,
    model = st.session_state.openai_model,
    base_url=st.session_state.openai_base_url
)

# Create the Embedding model

from langchain_openai import OpenAIEmbeddings


embeddings = OpenAIEmbeddings(
    openai_api_key = st.session_state.openai_api_key,
)