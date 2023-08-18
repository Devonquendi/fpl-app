import numpy as np
import streamlit as st


st.set_page_config(
    page_title='FPL Player Details', page_icon='👕', layout='wide')

fpl_data = st.session_state['data']
gameweeks = st.session_state['data'].gameweeks_df
teams = st.session_state['data'].teams_df
players = st.session_state['data'].players_df

# -------------------------------------------------------------------- side bar
# position slicer
position_select = st.sidebar.multiselect(
    'Position',
    players['pos'].unique()
)
if position_select:
    df = players[players['pos'].isin(position_select)]
# team slicer
team_select = st.sidebar.multiselect(
    'Team',
    players['team'].unique()
)
if team_select:
    df = players[players['team'].isin(team_select)]
# price slicer
price_max = st.sidebar.selectbox(
    'Max price',
    np.arange(14.5, 3.5, -0.5)
)
if price_max:
    df = players[players['£'] <= price_max]
# player selector
player_select = st.sidebar.radio(
    'Player',
    players['name'].unique()
)
selected_player_df = players[
    players['name'] == player_select]
selected_player_id = players[
    players['name'] == player_select]['player_id'].tolist()[0]

selected_player_history = fpl_data.get_player_summary(
    selected_player_id, type='history')
selected_player_history_past = fpl_data.get_player_summary(
    selected_player_id, type='history_past')
