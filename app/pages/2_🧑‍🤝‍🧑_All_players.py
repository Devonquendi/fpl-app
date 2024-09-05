import numpy as np
import plotly.express as px
import streamlit as st
from styles import style_players
from utils import donate_message, load_data

st.set_page_config(page_title="FPLstat: All players", page_icon="🧑‍🤝‍🧑", layout="wide")

st.title("All Players")

# load data from API
fpl_data = load_data()
# filter out players who have played less than 50 minutes
df = fpl_data.players_df.query("MP > 50").sort_values("Pts", ascending=False)

# -------------------------------------------------------------------- side bar
# team slicer
team_select = st.sidebar.multiselect("Team", df["team"].unique())
if team_select:
    team_filter = df["team"].isin(team_select)
    df = df[team_filter]
# position slicer
position_select = st.sidebar.multiselect("Position", df["pos"].unique())
if position_select:
    pos_filter = df["pos"].isin(position_select)
    df = df[pos_filter]
# price slicer
price_max = st.sidebar.selectbox("Max price", np.arange(15.5, 3.5, -0.5))
if price_max:
    price_filter = df["£"] <= price_max
    df = df[price_filter]

# -------------------------------------------------------------- main container
# ---------------------------------------------------- table
st.write("Click on columns for sorting")
st.dataframe(
    df.set_index(["pos", "team", "player_name", "£"]),
    column_order=[key for key in style_players.keys()],
    column_config=style_players,
)

# --------------------------------------------------- plots
st.header("Which players are the most clinical?")
with st.expander("What are the lines below?"):
    st.write(
        """The trendlines show the averaage relationship between xGI90 and GI90 for 
        each position.\n\nPlayers above the line, are more clinical than average in 
        their position"""
    )

max_axis = np.ceil(df["GS90"].max())
fig = px.scatter(
    df,
    x="xG90",
    y="GS90",
    size="£",
    color="pos",
    hover_name="player_name",
    trendline="ols",
    title="xG90 vs G90",
    range_x=[-0.1, max_axis],
    range_y=[-0.1, max_axis],
    width=1000,
    height=1000,
)

st.plotly_chart(fig, theme="streamlit")

donate_message()
