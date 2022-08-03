import altair as alt
import pandas as pd
import streamlit as st

from load_data import get_fpl_data

# load data from github
with st.spinner('Loading data from GitHub'):
    players, positions, teams, df = get_fpl_data()

# user id input
st.sidebar.text_input('Your FPL ID', key='fpl_id')
st.sidebar.write('Your team id:', st.session_state.fpl_id)

# side bar
position_multiselect = st.sidebar.multiselect(
    'Show positions',
    positions['position_name']
)
price_slider = st.sidebar.slider(
    'Price range', min_value=4.0, max_value=13.5, value=13.5, step=0.5
)

if position_multiselect:
    df = df[df['pos'].isin(position_multiselect)]
if price_slider:
    df = df[df['price'] <= price_slider]

# show table of players
# format float columns to 1 decimal place
float_cols = df.select_dtypes(include='float64').columns.values
st.write(df.style.format(subset=float_cols, formatter='{:.1f}'))

# scatter plot
c = alt.Chart(df).mark_circle().encode(
    x='ICT', y='PP90', size='price', color='pos', tooltip=['name', 'P'])

st.altair_chart(c, use_container_width=True)