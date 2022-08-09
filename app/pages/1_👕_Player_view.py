import numpy as np
import pandas as pd
import streamlit as st

from st_helpers import display_frame


st.set_page_config(
    page_title='FPL Player Details', page_icon='👕', layout='wide')

st.markdown('''
    #### To Do
      * Use metric elements to show per game statistics compared to overall position average
      * Weekly Pts chart
      * Weekly ICT chart
      * Nearest neighbours analysis to show "similar players"
      * Add total points and cost to player select in sidebar
      * Show player performance vs opposition strength ("fixture-proof" players)''')

fpl_data = st.session_state['data']
players = st.session_state['data'].players
positions = st.session_state['data'].positions
teams = st.session_state['data'].teams
df = st.session_state['data'].df_total
df_90 = st.session_state['data'].df_90
df_gp = st.session_state['data'].df_gp

# --------------------------------------------------------------------- side bar
# position slicer
position_select = st.sidebar.multiselect(
    'Position',
    df['pos'].unique()
)
if position_select:
    df = df[df['pos'].isin(position_select)]
# team slicer
team_select = st.sidebar.multiselect(
    'Team',
    df['team'].unique()
)
if team_select:
    df = df[df['team'].isin(team_select)]
# price slicer
price_max = st.sidebar.selectbox(
    'Max price',
    np.arange(13.5, 3.5, -0.5)
)
if price_max:
    df = df[df['£'] <= price_max]
# player selector
player_select = st.sidebar.radio(
    'Player',
    df['name'].unique()
)
selected_player_id = df[df['name']==player_select].index.tolist()[0]
player_history, player_history_past = fpl_data.get_player_summary(
    selected_player_id)

# --------------------------------------------------------------- main container
player_info = players.loc[selected_player_id].to_dict()
player_name = player_info['first_name'] + ' ' + player_info['second_name']
player_pos = player_info['pos_name_long']
player_team = player_info['team_name_long']

col1, col2, col3 = st.columns(3)
with col1:
    st.header(player_name)
with col2:
    st.header(player_pos)
with col3:
    st.header(player_team)

st.header('Player summary')
# ------------------------------------ metrics
st.subheader('Season totals')
player_totals = df.loc[selected_player_id].to_dict()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label='Points scored', value=player_totals['Pts'])
with col2:
    st.metric(label='Price', value=f"£{player_totals['£']}")
with col3:
    st.metric(label='TSB', value=f"{player_totals['TSB%']}%")

st.subheader('Gameweek history')
display_frame(player_history.drop(['OPP_strength', 'OPP_ovr', 'OPP_att', 'OPP_def'], axis=1))
st.subheader('Season history')
display_frame(player_history_past)