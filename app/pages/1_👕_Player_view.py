import numpy as np
import streamlit as st


st.set_page_config(page_title='FPL Player Details', page_icon='👕', layout='wide')

players = st.session_state['data'].players
history = st.session_state['data'].history
df = st.session_state['summary']

# -------------------------------------------------------------------- side bar
# position slicer
position_select = st.sidebar.multiselect(
    'Position',
    players['pos'].unique()
)
if position_select:
    players = players[players['pos'].isin(position_select)]
    df = df[df['pos'].isin(position_select)]
# team slicer
team_select = st.sidebar.multiselect(
    'Team',
    players['team'].unique()
)
if team_select:
    players = players[players['team'].isin(team_select)]
# price slicer
price_max = st.sidebar.selectbox(
    'Max price',
    np.arange(13.5, 3.5, -0.5)
)
if price_max:
    players = players[players['£'] <= price_max]
# player selector
player_select = st.sidebar.radio(
    'Player',
    players['name'].unique()
)

# -------------------------------------------------------------------- metrics
df
gs_pos_avg = df['GS'].mean().round(2)
st.write(gs_pos_avg)

player_stats = df[df['name']==player_select]
gs_player = player_stats.iloc[0]['GS']

st.write(player_stats)
st.write(gs_player)

st.metric('Goals scored', gs_player, delta=f'{gs_player-gs_pos_avg:.2f}')

players[players['name']==player_select]
history