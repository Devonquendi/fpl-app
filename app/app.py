import altair as alt
import pandas as pd
import streamlit as st

from load_data import FplData


st.set_page_config(layout='wide')

# load data from github
with st.spinner('Loading data from GitHub'):
    fpl_data = FplData()
    players = fpl_data.players
    history = fpl_data.history
    # players, history, summary = get_fpl_data()

df = fpl_data.get_summary()

# user id input
st.sidebar.text_input('Your FPL ID', key='fpl_id')
st.sidebar.write('Your team id:', st.session_state.fpl_id)

# side bar
position_multiselect = st.sidebar.multiselect(
    'Show positions',
    players['pos'].unique()
)
price_slider = st.sidebar.slider(
    'Price range', min_value=4.0, max_value=13.5, value=13.5, step=0.5
)

if position_multiselect:
    df = df[df['pos'].isin(position_multiselect)]
if price_slider:
    df = df[df['£'] <= price_slider]

# show table of players
# format float columns to 1 decimal place
st.write('Player summary')
float_cols = df.select_dtypes(include='float64').columns.values
st.write(df.style.format(subset=float_cols, formatter='{:.1f}'))

# scatter plot
c = alt.Chart(df).mark_circle().encode(
    x='II', y='Pts/GP', size='£', color='pos', tooltip=['name', 'Pts'])

st.altair_chart(c, use_container_width=True)
