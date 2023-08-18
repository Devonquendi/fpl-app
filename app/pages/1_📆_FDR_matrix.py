import streamlit as st
from st_helpers import style_background_team_fdr


st.set_page_config(
    page_title='FPL Team Fixtures', page_icon='📆', layout='wide')

fpl_data = st.session_state['data']
gameweeks = st.session_state['data'].gameweeks_df
teams = st.session_state['data'].teams_df

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
st.subheader('Fixtures')
st.dataframe(
    fixtures.style.applymap(style_background_team_fdr),
    use_container_width=True
)
