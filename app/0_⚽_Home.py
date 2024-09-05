import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="FPLstat: Home", page_icon="⚽", layout="wide")

st.title("FPL Dashboard")

st.write(
    """The FPL Dashboard is a collection of visualizations and insights using
     the Fantasy Premier League API data."""
)

st.markdown(
    """## 🛣️ Roadmap
* Include option to change FDR matrix to attack / defensive difficulty
* Optimal rotating pairs of players / teams for upcoming weeks
* Player time series chart showing GI vs xGI per gameweek

## 🤙 Contact
If you have any feedback or suggestions, feel free to send me an email at 
contactjamesleslie@gmail.com"""
)

components.iframe('<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdxqBjzjBtQxE4lcHp0LsORBTr6O1_kq4tvUwlZqF8l3u-SXA/viewform?embedded=true" width="640" height="737" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>', height=500)
