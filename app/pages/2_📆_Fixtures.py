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
teams = st.session_state['data'].teams

teams

fixtures = fpl_data.get_fixtures()
fixtures