import numpy as np
import plotly.express as px
import streamlit as st
from styles import style_background_player_fdr
from utils import donate_message, load_data

st.set_page_config(page_title="FPL Player Details", page_icon="👕", layout="wide")


# load data from API
fpl_data = load_data()

gameweeks = fpl_data.gameweeks_df
teams = fpl_data.teams_df
players = fpl_data.players_df.sort_values("Pts", ascending=False)

# -------------------------------------------------------------------- side bar
# position slicer
position_select = st.sidebar.multiselect("Position", players["pos"].unique())
if position_select:
    players = players[players["pos"].isin(position_select)]
# team slicer
team_select = st.sidebar.multiselect("Team", players["team"].unique())
if team_select:
    players = players[players["team"].isin(team_select)]
# price slicer
price_max = st.sidebar.selectbox("Max price", np.arange(14.5, 3.5, -0.5))
if price_max:
    players = players[players["£"] <= price_max]
# player selector
player_select = st.sidebar.radio("Player", players["player_name"].values)
selected_player_id = players[players["player_name"] == player_select].index.tolist()[0]

df = fpl_data.get_player_summary(selected_player_id, type="history")

df_past = fpl_data.get_player_summary(selected_player_id, type="history_past")
df["GI"] = df["GS"] + df["A"]
df["GI delta"] = df["GI"] - df["xGI"]

# ---------------------------------------------------------------main container
player_info = players.loc[selected_player_id].to_dict()
player_name = player_info["first_name"] + " " + player_info["second_name"]
player_pos = player_info["pos"]
player_team = player_info["team"]

st.header(player_name)
st.subheader(f"{player_pos} - {player_team}")

# ------------------------------------ metrics
st.subheader("Season totals")
player_totals = players.loc[selected_player_id].to_dict()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(label="Price", value=f"£{player_totals['£']}")
with col2:
    st.metric(label="PPG", value=player_totals["PPG"])
with col3:
    st.metric(label="xGI90", value=player_totals["xGI90"])
with col4:
    st.metric(label="xGC90", value=player_totals["xGC90"])
with col5:
    st.metric(label="TSB", value=f"{player_totals['TSB%']}%")

# ------------------------------------ upcoming fixtures
st.subheader("Upcoming fixtures")

player_fixtures = fpl_data.get_player_summary(selected_player_id, "fixtures")
st.dataframe(
    player_fixtures.T.style.map(style_background_player_fdr), use_container_width=True
)

# ------------------------------------ past performance
st.subheader("Past performance")
st.dataframe(df.sort_index(ascending=False), use_container_width=True)

fig = px.bar(
    df,
    y="GI delta",
    color="GI delta",
    color_continuous_scale="RdYlGn",
    color_continuous_midpoint=0,
    title="GI - xGI delta (positive numbers = 'overperforming')",
)
# fig.update_traces(marker_color=df["colour"])
st.plotly_chart(fig)


# plot cummulative xGI
fig = px.line(
    df[["xGI", "GI"]].cumsum(),
    title="Cummulative xGI and GI over time",
)
st.plotly_chart(fig)

donate_message()
