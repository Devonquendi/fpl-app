import pandas as pd
import requests
from tqdm.auto import tqdm
import os


BASE_URL = 'https://fantasy.premierleague.com/api/'


def get_player_gameweek_history(player_id):
    '''Get all gameweek info for a given player_id'''
    
    # send GET request to BASE_URL/api/element-summary/{PID}/
    data = requests.get(
            BASE_URL + 'element-summary/' + str(player_id) + '/').json()
    
    # extract 'history' data from response into dataframe
    df = pd.json_normalize(data['history'])
    
    return df


class FplApiData:
    
    def __init__(self, team_id, gw):
        '''Downloads all relevant data from FPL API'''
        
        # Bootstrap-static data
        api_data = requests.get(BASE_URL+'bootstrap-static/').json()
        # Manager data
        manager_data = requests.get(
            f'{BASE_URL}entry/{team_id}/event/{gw}/picks/').json()
        
        # player data
        self.players = pd.DataFrame(api_data['elements'])[
            ['first_name', 'second_name', 'web_name', 'id', 'team',
             'total_points', 'element_type', 'now_cost', 'points_per_game',
             'minutes', 'goals_scored', 'assists', 'clean_sheets',
             'goals_conceded', 'own_goals', 'penalties_saved',
             'penalties_missed', 'yellow_cards', 'red_cards', 'saves', 'bonus',
             'bps', 'influence', 'creativity', 'threat', 'ict_index']
        ]
        self.players.rename(columns={
            'id': 'player_id',
            'team': 'team_id',
            'element_type': 'position_id'}, inplace=True
        )
        self.players.set_index(['player_id'], inplace=True)
        # position data
        self.positions = pd.DataFrame(api_data['element_types']).drop(
            ['plural_name', 'plural_name_short', 'ui_shirt_specific',
             'sub_positions_locked', 'element_count'], axis=1)
        self.positions.rename(columns={
            'id': 'position_id',
            'singular_name_short': 'position_name'}, inplace=True)
        self.positions.set_index(['position_id'], inplace=True)
        # team data
        self.teams = pd.DataFrame(api_data['teams']).drop(
            ['code', 'played', 'form', 'win', 'draw', 'loss', 'points',
            'position', 'team_division', 'unavailable', 'pulse_id'], axis=1)
        self.teams.rename(columns={
            'id': 'team_id',
            'name': 'team_name'}, inplace=True)
        self.teams.set_index(['team_id'], inplace=True)
        # manager's current squad
        self.current_squad = pd.DataFrame(manager_data['picks'])
        self.current_squad.rename(columns={'element': 'player_id'}, inplace=True)
        # cash in the bank
        self.bank = manager_data['entry_history']['bank'] / 10

    
    def make_opt_df(self, forecasts_file):

        forecasts = pd.read_csv(forecasts_file)
        # rename columns to match api data
        forecasts.rename(columns={
            'Pos': 'position_name',
            'Name': 'web_name',
            'Team': 'team_name'}, inplace=True)
        forecasts.columns = forecasts.columns.str.lower()
        # replace position names with api names
        forecasts['position_name'].replace(
            {'G': 'GKP', 'D': 'DEF', 'M': 'MID', 'F': 'FWD'}, inplace=True)

        df = self.players[
            ['web_name', 'position_id', 'team_id', 'now_cost']
        ].reset_index().merge(
            self.teams[
                ['team_name']],
            on='team_id'
        ).merge(
            self.positions[
                ['position_name']],
            on='position_id'
        ).merge(
            forecasts, on=['team_name', 'web_name', 'position_name']
        )

        return df.sort_values('player_id')


    def make_points_df(self):
        '''Create dataframe with all players' inidividual gameweek scores'''

        tqdm.pandas()

        # get gameweek histories for each player
        df = self.players['id'].progress_apply(get_player_gameweek_history)

        # combine results into single dataframe
        df = pd.concat(p for p in df)

        # rename columns
        df.rename({'element':'player_id'}, axis=1, inplace=True)

        return df


    def transform_positions(self):

        '''Tranforms positions dataframe for use with optimisation model'''

        positions = self.positions.copy()
        positions['Pos'] = positions['singular_name'].str[0]
        positions.set_index('Pos', inplace=True)
        positions = positions[
            ['squad_select', 'squad_min_play' ,'squad_max_play']
        ]

        return positions


if __name__ == '__main__':

    # for testing

    data = FplApiData(team_id=384484, gw=36)

    df = data.make_opt_df(os.path.join('..', 'data', 'fplreview', 'gw37-38.csv'))

    print(df)


