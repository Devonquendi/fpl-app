from fpl_data.transform import FplApiDataTransformed
import streamlit as st


@st.cache_resource(ttl=3600)
def load_data():
    '''Load and cache data from FPL API'''
    return FplApiDataTransformed()


def display_frame(df):
    '''Modifies the default rendering of Pandas DataFrames
       - displays DataFrames with float columns rounded to 1 decimal place'''
    float_cols = df.select_dtypes(include='float64').columns.values
    st.dataframe(df.style.format(subset=float_cols, formatter='{:.1f}'))


def style_background_team_fdr(cell_value):
    '''Used to apply background highlighting to the teams FDR matrix'''

    bg = 'background-color:'
    team_str = 0

    if cell_value != '':
        team_str = int(cell_value[-1])

    if team_str == 1:
        return f'{bg} darkgreen;'
    elif team_str == 2:
        return f'{bg} #09fc7b;'
    elif team_str == 3:
        return f'{bg} #e7e7e8;'
    elif team_str == 4:
        return f'{bg} #ff1651; color: #ffffff;'
    elif team_str == 5:
        return f'{bg} #80072d; color: #ffffff;'
    else:
        return ''


def style_background_player_fdr(cell_value):
    '''Used to apply background highlighting to the player FDR matrix'''

    bg = 'background-color:'

    if cell_value == 1:
        return f'{bg} darkgreen;'
    elif cell_value == 2:
        return f'{bg} #09fc7b;'
    elif cell_value == 3:
        return f'{bg} #e7e7e8;'
    elif cell_value == 4:
        return f'{bg} #ff1651; color: #ffffff;'
    elif cell_value == 5:
        return f'{bg} #80072d; color: #ffffff;'
    else:
        return ''
