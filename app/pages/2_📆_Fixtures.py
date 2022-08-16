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

fixture_ratings, fixture_team_ids, fixture_team_names = fpl_data.get_fixtures()

st.subheader('Teams')
teams
st.subheader('Gameweeks')
gameweeks
st.subheader('Fixtures')
fixture_ratings
fixture_team_ids
fixture_team_names