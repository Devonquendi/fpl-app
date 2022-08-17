import numpy as np
import pandas as pd
import streamlit as st

from st_helpers import display_frame


st.set_page_config(
    page_title='FPL Team Fixtures', page_icon='📆', layout='wide')

st.markdown('''
    #### To Do
      * Create matrix of teams (rows) vs fixtures (columns)
      * Sort rows in order of easiest to hardest schedules''')

fpl_data = st.session_state['data']
gameweeks = st.session_state['data'].gameweeks
teams = st.session_state['data'].teams

# get next gameweek number from gameweeks df
NEXT_GW = gameweeks[gameweeks['is_next']].index.tolist()[0]

# --------------------------------------------------------------------- side bar
# position slicer
gw_slider = st.sidebar.slider(
    label='Gameweek range',
    min_value=int(gameweeks.index.min()),
    max_value=int(gameweeks.index.max()),
    value=(NEXT_GW, NEXT_GW+10)
)

start_gw, end_gw = gw_slider

st.write('Gameweeks:', gw_slider)

# get fixtures between chosen gameweek range
fixture_ratings, fixture_team_ids, fixture_team_names = fpl_data.get_fixtures(start_gw, end_gw)

# --------------------------------------------------------------- main container

st.subheader('Teams')
teams
st.subheader('Gameweeks')
gameweeks
gameweeks[gameweeks['is_next']]
NEXT_GW
st.subheader('Fixtures')
st.write('Team ids')
fixture_team_ids
st.write('Team ratings')
fixture_ratings
st.write('Team names')
fixture_team_names