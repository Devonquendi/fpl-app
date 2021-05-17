import pandas as pd
import requests
from tqdm.auto import tqdm


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

    # ToDo: join FplReview data and API data

    '''Downloads all relevant data from FPL API'''
    
    def __init__(self, team_id, gw):
        
        # Bootstrap-static data
        api_data = requests.get(BASE_URL+'bootstrap-static/').json()
        # player data
        self.players = pd.DataFrame(api_data['elements'])[
            ['first_name', 'second_name', 'web_name', 'id', 'team',
             'total_points', 'dreamteam_count', 'element_type', 'in_dreamteam',
             'now_cost', 'points_per_game', 'minutes', 'goals_scored',
             'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
             'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards',
             'saves', 'bonus', 'bps', 'influence', 'creativity', 'threat',
             'ict_index', 'influence_rank', 'influence_rank_type',
             'creativity_rank', 'creativity_rank_type', 'threat_rank',
             'threat_rank_type', 'ict_index_rank', 'ict_index_rank_type']
        ]
        # position data
        self.positions = pd.DataFrame(api_data['element_types']).drop(
            ['plural_name', 'plural_name_short', 'ui_shirt_specific',
             'sub_positions_locked'], axis=1)
        # team data
        self.teams = pd.DataFrame(api_data['teams']).drop(
            ['code', 'draw', 'form', 'loss', 'points', 'position',
            'team_division', 'unavailable', 'pulse_id'], axis=1)

        # Manager data
        manager_data = requests.get(
            f'{BASE_URL}entry/{team_id}/event/{gw}/picks/').json()
        # manager's current squad
        self.current_squad = pd.DataFrame(manager_data['picks'])
        # cash in the bank
        self.bank = manager_data['bank'] / 10


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




