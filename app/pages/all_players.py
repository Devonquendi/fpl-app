import numpy as np
import plotly.express as px
import streamlit as st
from styles import style_players
from utils import donate_message, load_data

st.set_page_config(page_title="FPLstat: All players", page_icon="🧑‍🤝‍🧑", layout="wide")

# load data from API
fpl_data = load_data()
# filter out players who have played less than 50 minutes
df = fpl_data.players_df.query("MP > 50").sort_values("Pts", ascending=False)

# ---------------------------------------------------- filters
# Create a four-column layout
col1, col2, col3, col4 = st.columns(4)

# team slicer
team_select = col1.multiselect("Team", np.sort(df["team"].unique()))
if team_select:
    team_filter = df["team"].isin(team_select)
    df = df[team_filter]
# position slicer
position_select = col2.multiselect("Position", df["pos"].unique())
if position_select:
    pos_filter = df["pos"].isin(position_select)
    df = df[pos_filter]
# price slicer
price_max = col3.number_input("Max price", value=df["£"].max(), step=0.1, format="%.1f")
if price_max:
    price_filter = df["£"] <= price_max
    df = df[price_filter]
# minutes played slicer
mp_min = col4.number_input("Minutes played >=", value=90, step=10)
if mp_min:
    mp_filter = df["MP"] >= mp_min
    df = df[mp_filter]

# ---------------------------------------------------- table
st.header("Player stats")
st.write("Click on columns for sorting")
st.dataframe(
    df.set_index(["pos", "team", "player_name", "£"]),
    column_order=[key for key in style_players.keys()],
    column_config=style_players,
)

# --------------------------------------------------- plots
st.header("Scatter plot")

c1, c2, c3 = st.columns([2, 2, 1])
x_var = c1.selectbox("X-axis", ["xG", "xA", "xGI", "I", "C", "T", "II"]) + "90"
y_var = c2.selectbox("Y-axis", ["GS", "A", "GI", "Pts"]) + "90"
axis_scale = c3.radio("Axis scale", ["Dynamic", "Square"])

if axis_scale == "Square":
    max_value = 1.1 * df[[x_var, y_var]].max().max()
    axis_range = [-0.1, max_value]
else:
    axis_range = [None, None]

with st.expander("Legend"):
    st.write("GS - Goals scored")
    st.write("A - Assists")
    st.write("GI - Goal Involvements (G + A)")
    st.write("I - Influence")
    st.write("C - Creativity")
    st.write("T - Threat")
    st.write("II - ICT Index")

fig = px.scatter(
    df,
    x=x_var,
    y=y_var,
    size="£",
    color="pos",
    hover_name="player_name",
    trendline="ols",
    title=f"{y_var} vs {x_var}",
    range_x=axis_range,
    range_y=axis_range,
    width=800,
    height=800,
)

st.plotly_chart(fig, use_container_width=True, theme="streamlit")

with st.expander("What are the lines above?"):
    st.write(
        """The trendlines show the average relationship between X and Y variables for 
        each position.\n\nPlayers above the line, are better than average in 
        their position"""
    )


donate_message()
