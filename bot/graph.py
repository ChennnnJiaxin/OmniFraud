import streamlit as st

# Connect to Neo4j
from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph(
    url=st.session_state.neo4j_uri,
    username=st.session_state.neo4j_username,
    password=st.session_state.neo4j_password,
    database=st.session_state.neo4j_database,
    refresh_schema=False,
)