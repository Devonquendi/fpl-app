import altair as alt
import numpy as np
import streamlit as st
from st_helpers import load_data, display_frame


st.set_page_config(
    page_title='FPL dashboard', page_icon='⚽', layout='wide')

# load data from API
fpl_data = load_data()
st.session_state['data'] = fpl_data

players = st.session_state['data'].players_df.rename(
    columns={'player_name': 'name'}
)

df = players.drop(
    ['Pts90', 'GS90', 'A90', 'GI90', 'xG90', 'xA90', 'xGI90', 'GC90', 'xGC90',
     'S90', 'BPS90', 'II90', 'first_name', 'second_name'],
    axis=1
).sort_values(
    'Pts',
    ascending=False
)

df_90 = players.drop(
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
    np.arange(14.5, 3.5, -0.5)
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
st.write('Click on columns for sorting')

tab1, tab2 = st.tabs(['Season totals', 'Totals per 90 minutes'])
with tab1:
    st.subheader('Season totals')
    display_frame(df)
with tab2:
    st.subheader('Totals per 90 minutes')
    display_frame(df_90)
    # ------------------------------------------------- scatter plots
    scatter_x_select = st.selectbox(
        'X axis variable',
        ['xG', 'xA', 'xGI', 'ICT Index', 'Influence', 'Creativity', 'Threat']
    )
    scatter_x_lookup = {
        'xG': 'xG90',
        'xA': 'xA90',
        'xGI': 'xGI90',
        'Influence': 'I90',
        'Creativity': 'C90',
        'Threat': 'T90',
        'ICT Index': 'II90'
    }

    scatter_y_select = st.selectbox(
        'Y axis variable',
        ['GS', 'xG', 'A', 'xA', 'GI', 'xGI']
    )

    scatter_y_lookup = {
        'GS': 'GS90',
        'xG': 'xG90',
        'A': 'A90',
        'xA': 'xA90',
        'GI': 'GI90',
        'xGI': 'xGI90'
    }

    scatter_x_var = scatter_x_lookup[scatter_x_select]
    scatter_y_var = scatter_y_lookup[scatter_y_select]

    st.subheader(f'{scatter_x_var} vs {scatter_y_var}')
    c = alt.Chart(df_90).mark_circle(size=75).encode(
        x=scatter_x_var,
        y=scatter_y_var,
        color='pos',
        tooltip=['name', scatter_x_var, scatter_y_var]
    )
    st.altair_chart(c, use_container_width=True)
