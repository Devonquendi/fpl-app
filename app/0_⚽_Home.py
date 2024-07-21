import streamlit as st
from st_helpers import load_data
import plotly.express as px

st.set_page_config(
    page_title='FPL dashboard', page_icon='⚽', layout='wide')

fpl_data = load_data()

players = fpl_data.players_df

st.title('FPL Dashboard')

st.write('This is some placeholder text description of the FPL Dashboard')

fig = px.scatter(
    players,
    x="GI",
    y="xGI",
    size="£",
    color="pos",
    hover_name="player_name",
    trendline="ols"
)

st.plotly_chart(fig, theme="streamlit", use_container_width=True)
