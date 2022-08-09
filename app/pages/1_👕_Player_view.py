import numpy as np
import streamlit as st

from load_data import get_player_history


st.set_page_config(
    page_title='FPL Player Details', page_icon='👕', layout='wide')

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
selected_player_df = df[df['name']==player_select]
selected_player_id = df[df['name']==player_select]['player_id'].tolist()[0]
selected_player_history = get_player_history(selected_player_id, type='history')
selected_player_history_past = get_player_history(selected_player_id, type='history_past')

# --------------------------------------------------------------- main container
st.header('Player summary')
st.subheader('Season totals')
selected_player_df
st.subheader('Gameweek history')
selected_player_history
st.subheader('Season history')
selected_player_history_past