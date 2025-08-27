import streamlit as st

st.set_page_config(
    page_title="FPLstat",
    # page_icon="https://at.govt.nz/favicon.ico",
    layout="wide",
)

pages = [
    st.Page("pages/all_players.py", title="All Players", icon="🧑‍🤝‍🧑", default=True),
    st.Page("pages/fdr_matrix.py", title="FDR Matrix", icon="📆"),
    st.Page("pages/individual_players.py", title="Individual players", icon="🧑‍🤝‍🧑"),
    st.Page("pages/about.py", title="About", icon="❓"),
]

pg = st.navigation(
    pages,
    position="top",
)
pg.run()
