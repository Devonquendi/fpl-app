import pandas as pd
import os, requests, time
from tqdm import tqdm


BASE_URL = 'https://fantasy.premierleague.com/api/'


def get_players_summary(api_data):
    '''Get all player summary data'''

    # load these columns from the 'elements' field
    df = pd.DataFrame(
        api_data['elements'])[
            ['id', 'first_name', 'second_name', 'web_name', 'team', 'element_type',
             'total_points', 'now_cost', 'points_per_game', 'form', 'value_form',
             'value_season', 'news', 'news_added', 'selected_by_percent', 'minutes',
             'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
             'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards', 'saves',
             'bonus','bps', 'influence', 'creativity', 'threat', 'ict_index', 'influence_rank',
             'creativity_rank', 'threat_rank', 'ict_index_rank']]
    # rename id columns
    df.rename(
        columns={'id':'player_id',
                 'team':'team_id',
                 'element_type':'position_id'},
        inplace=True)
    # some fields are returned as strings by the api
    df = df.astype({
        'points_per_game': 'float64',
        'influence': 'float64',
        'creativity': 'float64',
        'threat': 'float64',
        'ict_index': 'float64'})

    df.set_index('player_id', inplace=True)

    return df


def get_position_info(api_data):
    '''Get all position information'''

    df = pd.DataFrame(api_data['element_types'])
    
    df.drop(['plural_name', 'plural_name_short', 'ui_shirt_specific',
             'sub_positions_locked', 'element_count'],
            axis=1, inplace=True)
    
    df.rename(columns={'id':'position_id',
                       'singular_name_short':'position_name'},
              inplace=True)

    df.set_index('position_id', inplace=True)

    return df


def get_team_info(api_data):
    '''get information on all teams'''

    df = pd.DataFrame(api_data['teams'])

    df.drop(
        ['code', 'played', 'form', 'win', 'draw', 'loss', 'points', 'position',
         'team_division', 'unavailable', 'pulse_id'],
        axis=1, inplace=True)

    df.rename(columns={'id': 'team_id',
                       'name': 'team_name'},
              inplace=True)

    df.set_index('team_id', inplace=True)

    return df


def get_player_history(player_id, type):
    '''Get all past season info for a given player_id,
       wait between requests to avoid API rate limit'''

    success = False
    # try until a result is returned
    while not success:
        try:
            # send GET request to BASE_URL/api/element-summary/{PID}/
            data = requests.get(
                BASE_URL + 'element-summary/' + str(player_id) + '/').json()
            success = True
        except:
            # wait a bit to avoid API rate limits, if needed
            time.sleep(.3)
    
    # extract 'history_past' data from response into dataframe
    df = pd.json_normalize(data[type])

    # season history needs player id column added
    if type == 'history_past':
        df.insert(0, 'id', player_id)
    
    return df


class FplApiData:
    
    def __init__(self):
        '''Downloads all relevant data from FPL API'''
        
        # Bootstrap-static data
        api_data = requests.get(BASE_URL+'bootstrap-static/').json()
        
        # player data
        self.players = get_players_summary(api_data)
        # position data
        self.positions = get_position_info(api_data)
        # team data
        self.teams = get_team_info(api_data)



    def make_history_df(self, type):
        '''Create dataframe with all players' gameweek or season histories'''

        print(f'Creating player {type} dataframe')
        tqdm.pandas()

        # get histories for each player
        df = pd.Series(self.players.index).progress_apply(
            get_player_history, type=type)
        # combine results into single dataframe
        df = pd.concat(p for p in df)
        # rename columns
        df.rename({'element':'player_id'}, axis=1, inplace=True)

        return df
