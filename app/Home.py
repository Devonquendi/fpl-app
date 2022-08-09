import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from load_data import FplElementsData
from st_helpers import display_frame


st.set_page_config(
    page_title='FPL dashboard', page_icon='⚽', layout='wide')

st.markdown('''
    #### To Do
      * Scrape data from FBRef and Understat
      * Player points predictions
      * Upcoming fixture difficulties (who has easy/hard schedules?)''')

# load data from API
with st.spinner():
    fpl_data = FplElementsData()
    st.session_state['data'] = fpl_data

df = st.session_state['data'].df_total
df_90 = st.session_state['data'].df_90
df_gp = st.session_state['data'].df_gp

# --------------------------------------------------------------------- side bar
position_select = st.sidebar.multiselect(
    'Position',
    df['pos'].unique()
)
team_select = st.sidebar.multiselect(
    'Team',
    df['team'].unique()
)
price_max = st.sidebar.selectbox(
    'Max price',
    np.arange(13.5, 3.5, -0.5)
)
if team_select:
    team_filter = df['team'].isin(team_select)
    df = df[team_filter]
    df_90 = df_90[team_filter]
    df_gp = df_gp[team_filter]
if position_select:
    pos_filter = df['pos'].isin(position_select)
    df = df[pos_filter]
    df_90 = df_90[pos_filter]
    df_gp = df_gp[pos_filter]
if price_max:
    price_filter = df['£'] <= price_max
    df = df[price_filter]
    df_90 = df_90[price_filter]
    df_gp = df_gp[price_filter]

# --------------------------------------------------------------- main container
# ---------------------------------------------------- dataframes
st.header('Players summary')

st.subheader('Season totals')
display_frame(df)

st.subheader('Totals per game played')
display_frame(df_gp)

st.subheader('Totals per 90 minutes')
display_frame(df_90)
# ------------------------------------------------- scatter plots
scatter_x_var = st.selectbox(
    'X axis variable',
    ['ICT Index', 'Influence', 'Creativity', 'Threat']
)
scatter_lookup = {
    'Influence': 'I', 'Creativity': 'C', 'Threat': 'T', 'ICT Index': 'II'
}

col1, col2 = st.columns(2)
with col1:
    st.header('Points per game played')
    c = alt.Chart(df_gp).mark_circle(size=75).encode(
        x=scatter_lookup[scatter_x_var],
        y='Pts',
        color='pos',
        tooltip=['name', 'Pts']
    )
    st.altair_chart(c, use_container_width=True)
with col2:
    st.header('Points per 90')
    c = alt.Chart(df_90).mark_circle(size=75).encode(
        x=scatter_lookup[scatter_x_var],
        y='Pts',
        color='pos',
        tooltip=['name', 'Pts']
    )
    st.altair_chart(c, use_container_width=True)
