import pandas as pd
import streamlit as st
import time


@st.cache
def get_fpl_data():

    data_url_base = 'https://raw.githubusercontent.com/datahounds/fantasy-premier-league/master/data/2022-23/'

    players = pd.read_csv(data_url_base + 'players.csv')
    positions = pd.read_csv(data_url_base + 'positions.csv')
    teams = pd.read_csv(data_url_base + 'teams.csv')

    df = players.merge(teams, on='team_id').merge(positions, on='position_id')
    df = df[df['minutes']>270]

    df = df[
        ['player_id', 'web_name', 'short_name', 'position_name', 'now_cost',
        'total_points', 'points_per_game', 'minutes', 'goals_scored',
        'penalties_missed', 'assists', 'yellow_cards', 'red_cards', 'clean_sheets',
        'goals_conceded', 'saves', 'own_goals','penalties_saved', 'bonus', 'bps',
        'influence', 'creativity', 'threat', 'ict_index']
    ].sort_values(
        'total_points', ascending=False
    )

    df.columns = ['id', 'name', 'team', 'pos', 'price', 'P', 'PPG', 'M', 'GS', 'PM',
                'A', 'YC', 'RC', 'CS', 'GC', 'S', 'OG', 'PS', 'B', 'BPS', 'I',
                'C', 'T', 'ICT']

    # convert price to in-game values
    df['price'] = df['price'] / 10

    # convert ICT scores to per 90
    df[['I', 'C', 'T', 'ICT']] = df[['I', 'C', 'T', 'ICT']].divide(df['M'] / 90, axis=0)

    # add points per 90 column
    df['PP90'] = df['P'] / df['M'] * 90

    # testing out the spinner functionality
    time.sleep(2)
    
    return players, positions, teams, df
