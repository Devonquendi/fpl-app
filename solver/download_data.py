from argparse import ArgumentParser
import pandas as pd
import os
from datasets import FplApiData

# ToDo: replace this with ArgumentParser
DATA_DIR = os.path.join('..', 'data', '2020-21')


if __name__ == '__main__':
    
    # get all data from API
    api_data = FplApiData()
    # save all dataframes as CSVs in chosen folder
    api_data.players.to_csv(os.path.join(DATA_DIR, 'players.csv'))
    api_data.positions.to_csv(os.path.join(DATA_DIR, 'positions.csv'))
    api_data.teams.to_csv(os.path.join(DATA_DIR, 'teams.csv'))
    api_data.make_gameweek_history_df().to_csv(
        os.path.join(DATA_DIR, 'gameweek_history.csv'), index=False)
    api_data.make_gameweek_history_df().to_csv(
        os.path.join(DATA_DIR, 'season_history.csv'), index=False)
