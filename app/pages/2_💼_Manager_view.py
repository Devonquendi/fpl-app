from cmath import pi
import numpy as np
import streamlit as st

from load_data import FplManagerData
from st_helpers import display_frame


st.set_page_config(
    page_title='FPL Manager Details', page_icon='💼', layout='wide')

st.markdown('''
    #### To Do
      * Team name
      * Mini league ranks
      * Current / previous seasons' rank
      * Weekly scores
      * Your top performers
      * Top performing players **NOT** in your team''')

df = st.session_state['data'].df_total
df_90 = st.session_state['data'].df_90
df_gp = st.session_state['data'].df_gp

# --------------------------------------------------------------------- side bar
# user id input
manager_id = st.sidebar.text_input('Your FPL ID', value='414154', key='fpl_id')
st.sidebar.write('Your team id:', manager_id)

manager_data = FplManagerData(manager_id, gw=1)

picks = manager_data.picks.merge(
    df_gp, on='player_id'
)
# add captain and vice captain labels
picks['name'] = picks.apply(
    lambda x: x['name'] + ' (c)' if x['is_captain'] else x['name'], axis=1)
picks['name'] = picks.apply(
    lambda x: x['name'] + ' (v)' if x['is_vice_captain'] else x['name'], axis=1)
picks.drop(
    ['multiplier', 'is_captain', 'is_vice_captain'], axis=1, inplace=True)

# ------------------------------------------------------------------- main panel
st.subheader('Manager information')
st.subheader('Last week\'s team')
display_frame(picks)