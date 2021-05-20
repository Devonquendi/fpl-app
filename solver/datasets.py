import pandas as pd
import os, requests, time
from argparse import ArgumentParser
from tqdm.auto import tqdm


BASE_URL = 'https://fantasy.premierleague.com/api/'


def get_player_gameweek_history(player_id, wait_time=.3):
    '''Get all gameweek info for a given player_id
       wait between requests to avoid API rate limit'''
    
    # send GET request to BASE_URL/api/element-summary/{PID}/
    data = requests.get(
            BASE_URL + 'element-summary/' + str(player_id) + '/').json()
    # extract 'history' data from response into dataframe
    df = pd.json_normalize(data['history'])
    # avoid getting rate limited
    time.sleep(wait_time)
    
    return df


def get_player_season_history(player_id, wait_time=.3):
    '''Get all past season info for a given player_id,
       wait between requests to avoid API rate limit'''
    
    # send GET request to
    # fantasy.premierleague.com/api/element-summary/{PID}/
    r = requests.get(
        BASE_URL + 'element-summary/' + str(player_id) + '/').json()
    # extract 'history_past' data from response into dataframe
    df = pd.json_normalize(r['history_past'])
    df.insert(0, 'id', player_id)
    # avoid getting rate limited
    time.sleep(wait_time)
    
    return df


class FplApiData:
    
    def __init__(self, team_id=None, gw=None):
        '''Downloads all relevant data from FPL API'''
        
        # Bootstrap-static data
        api_data = requests.get(BASE_URL+'bootstrap-static/').json()
        
        # player data
        self.players = pd.DataFrame(
            api_data['elements'])[
                ['first_name', 'second_name', 'web_name', 'id', 'team',
                 'total_points', 'element_type', 'now_cost', 'points_per_game',
                 'minutes', 'goals_scored', 'assists', 'clean_sheets',
                 'goals_conceded', 'own_goals', 'penalties_saved', 
                 'penalties_missed', 'yellow_cards', 'red_cards', 'saves',
                 'bonus','bps', 'influence', 'creativity', 'threat', 'ict_index']]
        self.players.rename(columns={'id':'player_id',
                                     'team':'team_id',
                                     'element_type':'position_id'},
                            inplace=True)
        self.players.set_index(['player_id'], inplace=True)
        # position data
        self.positions = pd.DataFrame(api_data['element_types'])
        self.positions.drop(
            columns=['plural_name', 'plural_name_short', 'ui_shirt_specific',
                     'sub_positions_locked', 'element_count'],
            axis=1, inplace=True)
        self.positions.rename(columns={'id':'position_id',
                                       'singular_name_short':'position_name'},
                              inplace=True)
        self.positions.set_index(['position_id'], inplace=True)
        # team data
        self.teams = pd.DataFrame(api_data['teams'])
        self.teams.drop(
            columns=['code', 'played', 'form', 'win', 'draw', 'loss', 'points',
                     'position', 'team_division', 'unavailable', 'pulse_id'],
            axis=1, inplace=True)
        self.teams.rename(columns={'id': 'team_id',
                                   'name': 'team_name'},
                          inplace=True)
        self.teams.set_index(['team_id'], inplace=True)

        # Manager data
        if team_id != None and gw != None:
            manager_data = requests.get(
                f'{BASE_URL}entry/{team_id}/event/{gw}/picks/').json()
            # manager's current squad
            self.current_squad = pd.DataFrame(manager_data['picks'])
            self.current_squad.rename(columns={'element': 'player_id'},
                                      inplace=True)
            # cash in the bank
            self.bank = manager_data['entry_history']['bank'] / 10

    
    def make_opt_df(self, forecasts_file):

        forecasts = pd.read_csv(forecasts_file)
        # rename columns to match api data
        forecasts.rename(columns={'Pos': 'position_name',
                                  'Name': 'web_name',
                                  'Team': 'team_name'},
                         inplace=True)
        forecasts.columns = forecasts.columns.str.lower()
        # replace position names with api names
        forecasts['position_name'].replace(
            {'G':'GKP', 'D':'DEF', 'M':'MID', 'F':'FWD'}, inplace=True)

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

        df.set_index(['player_id'], inplace=True)

        return df


    def make_gameweek_history_df(self):
        '''Create dataframe with all players' inidividual gameweek scores'''

        tqdm.pandas()

        # get gameweek histories for each player
        df = pd.Series(self.players.index).progress_apply(
            get_player_gameweek_history)
        # combine results into single dataframe
        df = pd.concat(p for p in df)
        # rename columns
        df.rename({'element':'player_id'}, axis=1, inplace=True)

        return df


    def make_season_history_df(self):
        '''Create dataframe with all players' past season summaries'''

        tqdm.pandas()

        # get gameweek histories for each player
        df = pd.Series(self.players.index).progress_apply(
            get_player_season_history)
        # combine results into single dataframe
        df = pd.concat(p for p in df)
        # rename columns
        df.rename({'element':'player_id'}, axis=1, inplace=True)

        return df


if __name__ == '__main__':

    parser = ArgumentParser(description='Downloads all datasets from FPL API')
    parser.add_argument('-o', '--output_dir', 
                        default=os.path.join('..', 'data', '2020-21'),
                        help='relative path to output folder', type=str)
    args = parser.parse_args()

    # make sure using correct separators for path names
    data_dir = args.output_dir.replace('/', os.sep)
    
    # get all data from API
    api_data = FplApiData()
    # save all dataframes as CSVs in chosen folder
    api_data.players.to_csv(os.path.join(data_dir, 'players.csv'))
    api_data.positions.to_csv(os.path.join(data_dir, 'positions.csv'))
    api_data.teams.to_csv(os.path.join(data_dir, 'teams.csv'))
    api_data.make_gameweek_history_df().to_csv(
        os.path.join(data_dir, 'gameweek_history.csv'), index=False)
    api_data.make_gameweek_history_df().to_csv(
        os.path.join(data_dir, 'season_history.csv'), index=False)
