import pandas as pd
import streamlit as st

from datasets import FplApiData


@st.cache  # only hits the API once and stores the result in memory
def get_fpl_data():

    api_data = FplApiData()
    players = api_data.players
    positions = api_data.positions
    teams = api_data.teams

    df = players.merge(teams, on='team_id').merge(positions, on='position_id').reset_index()

    df = df[df['minutes']>270]

    df = df[
        ['web_name', 'short_name', 'position_name', 'now_cost',
        'total_points', 'points_per_game', 'minutes', 'goals_scored',
        'penalties_missed', 'assists', 'yellow_cards', 'red_cards', 'clean_sheets',
        'goals_conceded', 'saves', 'own_goals','penalties_saved', 'bonus', 'bps',
        'influence', 'creativity', 'threat', 'ict_index']
    ].sort_values(
        'total_points', ascending=False
    )

    df.columns = ['name', 'team', 'pos', 'price', 'P', 'PPG', 'M', 'GS', 'PM',
                'A', 'YC', 'RC', 'CS', 'GC', 'S', 'OG', 'PS', 'B', 'BPS', 'I',
                'C', 'T', 'ICT']

    # convert price to in-game values
    df['price'] = df['price'] / 10

    # convert ICT scores to per 90
    df[['I', 'C', 'T', 'ICT']] = df[['I', 'C', 'T', 'ICT']].divide(df['M'] / 90, axis=0)

    # add points per 90 column
    df['PP90'] = df['P'] / df['M'] * 90
    
    return players, positions, teams, df
