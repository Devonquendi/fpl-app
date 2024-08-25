import streamlit as st
from utils import load_data, donate_message
from styles import style_background_team_fdr


st.set_page_config(
    page_title='FDR Matrix', page_icon='📆', layout='wide')

# load data from API
fpl_data = load_data()
gameweeks = fpl_data.gameweeks_df
teams = fpl_data.teams_df

# get next gameweek number from gameweeks df
NEXT_GW = gameweeks[gameweeks['is_next']].index.tolist()[0]

# -------------------------------------------------------------------- side bar
# gameweek slicer
gw_slider = st.sidebar.slider(
    label='Gameweek range',
    min_value=int(gameweeks.index.min()),
    max_value=int(gameweeks.index.max()),
    value=(NEXT_GW, NEXT_GW+7)
)

start_gw, end_gw = gw_slider

# get fixtures between chosen gameweek range
fixtures = fpl_data.get_fixtures_matrix(
    start_gw, end_gw - start_gw)

# -------------------------------------------------------------- main container
st.header('Fixtures')
st.write(
    'Rows are sorted in ascending order of FDR - least difficult schedules'
    ' at the top.'
)

st.dataframe(
    fixtures.style.map(style_background_team_fdr),
    height=750,
    use_container_width=True
)
donate_message()
