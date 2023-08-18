import altair as alt
import numpy as np
import streamlit as st
from st_helpers import load_data, display_frame


st.set_page_config(
    page_title='FPL dashboard', page_icon='⚽', layout='wide')

st.markdown('''
    #### To Do
      * Scrape data from FBRef and Understat
      * Player points predictions
      * Upcoming fixture difficulties (who has easy/hard schedules?)
      * Differential picks''')

# load data from API
fpl_data = load_data()
st.session_state['data'] = fpl_data

df = st.session_state['data'].players_df.drop(
    ['Pts90', 'GS90', 'A90', 'GI90', 'xG90', 'xA90', 'xGI90', 'GC90', 'xGC90',
     'S90', 'BPS90', 'II90'],
    axis=1
).sort_values(
    'Pts',
    ascending=False
)

df_90 = st.session_state['data'].players_df.drop(
    ['Pts', 'GS', 'A', 'GI', 'xG', 'xA', 'xGI', 'GC', 'xGC', 'BPS', 'II'],
    axis=1
).sort_values(
    'Pts90',
    ascending=False
)
# filter based on minutes played per game
df_90 = df_90[df_90['MP'] > 20]

# -------------------------------------------------------------------- side bar
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
if position_select:
    pos_filter = df['pos'].isin(position_select)
    df = df[pos_filter]
    df_90 = df_90[pos_filter]
if price_max:
    price_filter = df['£'] <= price_max
    df = df[price_filter]
    df_90 = df_90[price_filter]

# -------------------------------------------------------------- main container
# ---------------------------------------------------- dataframes
st.header('Players summary')

st.subheader('Season totals')
display_frame(df)

st.subheader('Totals per 90 minutes')
display_frame(df_90)
# ------------------------------------------------- scatter plots
scatter_x_var = st.selectbox(
    'X axis variable',
    ['ICT Index', 'Influence', 'Creativity', 'Threat']
)
scatter_lookup = {
    'Influence': 'I90',
    'Creativity': 'C90',
    'Threat': 'T90',
    'ICT Index': 'II90'
}

col1, col2 = st.columns(2)
with col1:
    st.header('Points per 90')
    c = alt.Chart(df_90).mark_circle(size=75).encode(
        x=scatter_lookup[scatter_x_var],
        y='Pts90',
        color='pos',
        tooltip=['name', scatter_lookup[scatter_x_var], 'Pts90']
    )
    st.altair_chart(c, use_container_width=True)
with col2:
    st.header('xGI per 90')
    c = alt.Chart(df_90).mark_circle(size=75).encode(
        x=scatter_lookup[scatter_x_var],
        y='xGI90',
        color='pos',
        tooltip=['name', scatter_lookup[scatter_x_var], 'xGI90']
    )
    st.altair_chart(c, use_container_width=True)
