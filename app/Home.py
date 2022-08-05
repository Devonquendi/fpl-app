import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from load_data import FplData


st.set_page_config(page_title='FPL dashboard', page_icon='⚽', layout='wide')

# load data from github
with st.spinner('Loading data from GitHub'):
    fpl_data = FplData()
    st.session_state['summary'] = fpl_data.get_summary()
    st.session_state['data'] = fpl_data

players = st.session_state['data'].players
df = st.session_state['summary']

# -------------------------------------------------------------------- side bar
# user id input
st.sidebar.text_input('Your FPL ID', key='fpl_id')
st.sidebar.write('Your team id:', st.session_state.fpl_id)

position_select = st.sidebar.multiselect(
    'Position',
    players['pos'].unique()
)
team_select = st.sidebar.multiselect(
    'Team',
    players['team'].unique()
)
price_max = st.sidebar.selectbox(
    'Max price',
    np.arange(13.5, 3.5, -0.5)
)
if team_select:
    df = df[df['team'].isin(team_select)]
if position_select:
    df = df[df['pos'].isin(position_select)]
if price_max:
    df = df[df['£'] <= price_max]

# --------------------------------------------------------------- main container
# show table of players
# format float columns to 1 decimal place
st.header('Player summary')
float_cols = df.select_dtypes(include='float64').columns.values
st.dataframe(df.style.format(subset=float_cols, formatter='{:.1f}'))

scatter_x_var = st.selectbox(
    'X axis variable',
    ['Influence', 'Creativity', 'Threat', 'ICT Index']
)
scatter_90_lookup = {
    'Influence': 'I/90', 'Creativity': 'C/90', 'Threat': 'T/90',
    'ICT Index': 'II/90'
}
scatter_GP_lookup = {
    'Influence': 'I/GP', 'Creativity': 'C/GP', 'Threat': 'T/GP',
    'ICT Index': 'II/GP'
}

col1, col2 = st.columns(2)
with col1:
    st.header('Points per 90')
    c = alt.Chart(df).mark_circle(size=75).encode(
        x=scatter_90_lookup[scatter_x_var],
        y='Pts/90',
        color='pos',
        tooltip=['name', 'Pts/90']
    )
    st.altair_chart(c, use_container_width=True)
with col2:
    st.header('Points per game played')
    c = alt.Chart(df).mark_circle(size=75).encode(
        x=scatter_GP_lookup[scatter_x_var],
        y='Pts/GP',
        color='pos',
        tooltip=['name', 'Pts/GP']
    )
    st.altair_chart(c, use_container_width=True)
