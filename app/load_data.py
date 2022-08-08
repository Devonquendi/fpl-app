import numpy as np
import pandas as pd
import requests
import streamlit as st
import time

BASE_URL = 'https://fantasy.premierleague.com/api/'


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


# @st.cache
class FplData:
    
    def __init__(self):
        '''Loads all saved FPL API data from GitHub'''

        # get all data from fpl api
        api_data = requests.get(BASE_URL+'bootstrap-static/').json()

        # get position data
        positions = pd.DataFrame(
            api_data['element_types']
        ).drop(
            ['plural_name', 'plural_name_short', 'singular_name',
             'ui_shirt_specific', 'sub_positions_locked'],
            axis=1
        ).rename(columns={
            'id': 'position_id',
            'singular_name_short': 'pos',
            'element_count': 'count'}
        ).set_index(
            'position_id'
        )

        # get team data
        teams = pd.DataFrame(
            api_data['teams']
        ).drop(
            ['code', 'played', 'form', 'win', 'draw', 'loss', 'points',
             'position', 'team_division', 'unavailable', 'pulse_id'],
            axis=1
        ).rename(columns={
            'id': 'team_id',
            'short_name': 'team',
            'name': 'team_name_long'}
        ).set_index(
            'team_id'
        )

        # get player data
        players = pd.DataFrame(
            api_data['elements'])[[
                'id', 'first_name', 'second_name', 'web_name', 'team', 'element_type',
                'total_points', 'now_cost', 'points_per_game', 'form', 'value_form',
                'value_season', 'news', 'news_added', 'selected_by_percent', 'minutes',
                'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
                'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards', 'saves',
                'bonus','bps', 'influence', 'creativity', 'threat', 'ict_index', 'influence_rank',
                'creativity_rank', 'threat_rank', 'ict_index_rank']
            ].rename(columns={
                'id': 'player_id',
                'team': 'team_id',
                'element_type': 'position_id',
                'web_name': 'name',
                'total_points': 'Pts',
                'points_per_game': 'PPG',
                'now_cost': '£',
                'minutes': 'MP',
                'goals_scored': 'GS',
                'assists': 'A',
                'clean_sheets': 'CS',
                'goals_conceded': 'GC',
                'own_goals': 'OG',
                'penalties_saved': 'PS',
                'penalties_missed': 'PM',
                'yellow_cards': 'YC',
                'red_cards': 'RC',
                'saves': 'S',
                'bonus': 'B',
                'bps': 'BPS',
                'influence': 'I',
                'creativity': 'C',
                'threat': 'T',
                'ict_index': 'II',
                'selected_by_percent': 'TSB%'}
            ).astype({
                'PPG': 'float64',
                'I': 'float64',
                'C': 'float64',
                'T': 'float64',
                'II': 'float64'}
            ).set_index(
                'player_id'
            )

        # create summary df
        # exclude who haven't played any minutes
        df = players[players['MP'] > 0]
        # df = df[df['total_points'] > 0]
        df = df.merge(teams, on='team_id').merge(positions, on='position_id')

        # # infer the games played column from points / points_per_game
        df['GP'] = df['Pts'].divide(df['PPG']).fillna(0).round(0).astype('int')
        
        # drop columns we are not interested in
        df = df[
            ['name', 'team', 'pos', '£', 'Pts', 'GP', 'MP', 'GS', 'A',
             'CS', 'GC', 'OG', 'PS', 'PM', 'YC', 'RC', 'S', 'B', 'BPS', 'I',
             'C', 'T', 'II']
        ]

        df['£'] = df['£'] / 10

        score_cols = ['Pts', 'GS', 'A', 'CS', 'GC', 'OG', 'PS', 'PM', 'YC', 'RC', 'S', 'B', 'BPS',
            'I', 'C', 'T', 'II']
        # add "per 90" metrics
        df_90 = df.copy()
        df_90[score_cols] = df_90[score_cols].divide(df_90['MP'] / 90, axis=0)
        # add "per game" metrics
        df_gp = df.copy()
        df_gp[score_cols] = df_gp[score_cols].divide(df_gp['GP'], axis=0)

        # history = history.merge(teams, left_on='opponent_team', right_on='team_id')

        # # calculate opponent strength based on whether match was home or away
        # history['vs_ovr'] = (history['was_home'] * history['strength_overall_home']) + (~history['was_home'] * history['strength_overall_away'])
        # history['vs_att'] = (history['was_home'] * history['strength_attack_home']) + (~history['was_home'] * history['strength_attack_away'])
        # history['vs_def'] = (history['was_home'] * history['strength_defence_home']) + (~history['was_home'] * history['strength_defence_away'])
        # history['vs'] = history.apply(lambda s: s['short_name'] + ' (H)' if s['was_home'] else s['short_name'] + ' (A)', axis=1)

        # history = history[['player_id', 'round', 'vs', 'strength', 'vs_ovr', 'vs_att', 'vs_def',
        #         'total_points', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'goals_conceded',
        #         'own_goals', 'penalties_saved', 'bonus', 'bps', 'influence', 'creativity', 'threat',
        #         'ict_index', 'value', 'selected', 'transfers_balance']]

        # history.columns = ['player_id', 'GW', 'vs', 'vs_strength', 'vs_ovr', 'vs_att', 'vs_def', 'Pts', 'MP',
        #             'GS', 'A', 'CS', 'GC', 'OG', 'PS', 'B', 'BPS', 'I', 'C', 'T', 'II', '£', 'TSB', 'NT']

        # # convert price to in-game values
        # history['£'] = (history['£'] / 10).round(1)

        # # create game_played column
        # history['GP'] = history['MP'] > 0

        # history = pd.read_csv(data_url + 'gameweek_history.csv')

        # self.history = history
        self.teams = teams
        self.positions = positions
        self.players = players
        self.df_total = df.round(1).sort_values('Pts', ascending=False)
        self.df_90 = df_90.round(1).sort_values('Pts', ascending=False)
        self.df_gp = df_gp.round(1).sort_values('Pts', ascending=False)


