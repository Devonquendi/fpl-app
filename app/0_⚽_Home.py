import streamlit as st

st.set_page_config(page_title="FPLstat: Home", page_icon="⚽", layout="wide")

st.title("FPL Dashboard")

st.write(
    """The FPL Dashboard is a collection of visualizations and insights using
     the Fantasy Premier League API data."""
)

st.markdown(
    """# Roadmap
* Include option to change FDR matrix to attack / defensive difficulty
* Optimal rotating pairs of players / teams for upcoming weeks
* Player time series chart showing GI vs xGI per gameweek
"""
)
