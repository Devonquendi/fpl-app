import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from load_data import FplData


def display_frame(df):
    '''display dataframe with all float columns rounded to 1 decimal place'''
    float_cols = df.select_dtypes(include='float64').columns.values
    st.dataframe(df.style.format(subset=float_cols, formatter='{:.1f}'))


st.set_page_config(page_title='FPL dashboard', page_icon='⚽', layout='wide')

# load data from github
with st.spinner():
    fpl_data = FplData()
    st.session_state['data'] = fpl_data

df = st.session_state['data'].df_total
df_90 = st.session_state['data'].df_90
df_gp = st.session_state['data'].df_gp

# -------------------------------------------------------------------- side bar
# user id input
st.sidebar.text_input('Your FPL ID', key='fpl_id')
st.sidebar.write('Your team id:', st.session_state.fpl_id)

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
    df = df[df['£'] <= price_max]

# --------------------------------------------------------------- main container
# ---------------------------------------------------- dataframes
st.header('Player summary')

# info_cols = ['name', 'team', 'pos', '£', 'GP', 'MP']
# score_total_cols = ['Pts', 'GS', 'A', 'CS', 'B', 'BPS', 'I', 'C', 'T', 'II']
# score_90_cols = [c + '/90' for c in score_total_cols]
# score_gp_cols = [c + '/GP' for c in score_total_cols]

st.subheader('Season totals')
display_frame(df)

st.subheader('Totals per 90 minutes')
display_frame(df_90)

st.subheader('Totals per game played')
display_frame(df_gp)

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
    st.header('Points per 90')
    c = alt.Chart(df_90).mark_circle(size=75).encode(
        x=scatter_lookup[scatter_x_var],
        y='Pts',
        color='pos',
        tooltip=['name', 'Pts']
    )
    st.altair_chart(c, use_container_width=True)
with col2:
    st.header('Points per game played')
    c = alt.Chart(df_gp).mark_circle(size=75).encode(
        x=scatter_lookup[scatter_x_var],
        y='Pts',
        color='pos',
        tooltip=['name', 'Pts']
    )
    st.altair_chart(c, use_container_width=True)
