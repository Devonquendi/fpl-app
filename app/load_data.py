import numpy as np
import pandas as pd
import requests
import streamlit as st
import time

BASE_URL = 'https://fantasy.premierleague.com/api/'


# used to rename any occurence of the following columns
COLUMN_RENAME_LIST = {
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
    'selected_by_percent': 'TSB%'
}


class FplApiData:

    def __init__(self):
        '''Loads all FPL data from API'''

        # get all data from fpl api
        api_data = requests.get(BASE_URL+'bootstrap-static/').json()

        # get position data
        positions = pd.DataFrame(
            api_data['element_types']
        ).drop(
            ['plural_name', 'plural_name_short', 'ui_shirt_specific',
             'sub_positions_locked'],
            axis=1
        ).rename(columns={
            'id': 'position_id',
            'singular_name': 'pos_name_long',
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
            ].rename(columns=COLUMN_RENAME_LIST
            ).astype({
                'PPG': 'float64',
                'I': 'float64',
                'C': 'float64',
                'T': 'float64',
                'II': 'float64'}
            ).merge(
                teams[['team', 'team_name_long']], on='team_id'
            ).merge(
                positions[['pos', 'pos_name_long']], on='position_id'
            ).set_index(
                'player_id'
            )

        #  --------------------------------------------------- create summary df
        # exclude who haven't played any minutes
        df = players[players['MP'] > 0]
        # df = df.merge(teams, on='team_id').merge(positions, on='position_id')

        # # infer the games played column from points / points_per_game
        df['GP'] = df['Pts'].divide(df['PPG']).fillna(0).round(0).astype('int')
        
        # drop columns we are not interested in
        df = df[
            ['name', 'team', 'pos', '£', 'TSB%', 'Pts', 'GP', 'MP', 'GS', 'A',
             'CS', 'GC', 'OG', 'PS', 'PM', 'YC', 'RC', 'S', 'B', 'BPS', 'I',
             'C', 'T', 'II']
        ]

        # convert price to in-game values
        df['£'] = df['£'] / 10

        score_cols = ['Pts', 'GS', 'A', 'CS', 'GC', 'OG', 'PS', 'PM', 'YC',
                      'RC', 'S', 'B', 'BPS', 'I', 'C', 'T', 'II']
        # add "per 90" metrics
        df_90 = df.copy()
        df_90[score_cols] = df_90[score_cols].divide(
            df_90['MP'] / 90, axis=0
        ).fillna(0).replace(np.inf, 0)
        # add "per game" metrics
        df_gp = df.copy()
        df_gp[score_cols] = df_gp[score_cols].divide(
            df_gp['GP'], axis=0
        ).fillna(0).replace(np.inf, 0)

        self.teams = teams
        self.positions = positions
        self.players = players
        self.df_total = df.round(1).sort_values('Pts', ascending=False)
        self.df_90 = df_90.round(1).sort_values('Pts', ascending=False)
        self.df_gp = df_gp.round(1).sort_values('Pts', ascending=False)


    def get_player_summary(self, player_id):
        '''Get all current and past season history for a given player_id,
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
        
        # ----------------------------------------------------- gameweek history
        gameweek_history = pd.DataFrame(
            data['history']
        ).drop(
            ['transfers_in', 'transfers_out'], axis=1
        ).rename(columns=COLUMN_RENAME_LIST | {
            'element': 'player_id',
            'fixture': 'fixture_id',
            'opponent_team': 'team_id',
            'team_h_score': 'h_score',
            'team_a_score': 'a_score',
            'round': 'GW',
            'value': '£',
            'transfers_balance': 'NT',
            'selected': 'SB'}
        ).astype({
            'I': 'float64',
            'C': 'float64',
            'T': 'float64',
            'II': 'float64'}
        ).merge(
            self.teams.rename(columns={'strength': 'OPP_strength'}), on='team_id'
        )

        gameweek_history['£'] = gameweek_history['£']/10

        # add vs columns
        gameweek_history = gameweek_history.assign(
            OPP_ovr=lambda s: s['was_home'] * s['strength_overall_away'] + \
                ~s['was_home'] * s['strength_overall_home'],
            OPP_att=lambda s: s['was_home'] * s['strength_attack_away'] + \
                ~s['was_home'] * s['strength_attack_home'],
            OPP_def=lambda s: s['was_home'] * s['strength_defence_away'] + \
                ~s['was_home'] * s['strength_defence_home'],
            GP=lambda s: s['MP'] > 0
        )
        # add OPP column with team name, home/away status and score
        gameweek_history['OPP'] = gameweek_history.apply(
            lambda s: s['team'] + ' (H) ' + str(s['h_score']) + ' - ' + str(s['a_score']) if s['was_home']
                else s['team'] + ' (A) ' + str(s['h_score']) + ' - ' + str(s['a_score']), axis=1)

        gameweek_history = gameweek_history[[
            'GW', 'OPP', 'OPP_strength', 'OPP_ovr', 'OPP_att', 'OPP_def', 'Pts',
            'MP', 'GP', 'GS', 'A', 'CS', 'GC', 'OG', 'PS', 'PM', 'YC', 'RC', 'S',
            'B', 'BPS', 'I', 'C', 'T', 'II', 'NT', 'SB', '£'
        ]]

        # ------------------------------------------------------- season history
        season_history = pd.DataFrame(
            data['history_past']
        )
        # some players have not played any previous seasons in the PL
        if not season_history.empty:
            season_history = season_history.drop(
                'element_code', axis=1
            ).rename(columns=COLUMN_RENAME_LIST | {
                'season_name': 'season',
                'start_cost': '£S',
                'end_cost': '£E'}
            ).astype({
                'I': 'float64',
                'C': 'float64',
                'T': 'float64',
                'II': 'float64'}
            )

            season_history.insert(0, 'player_id', player_id)
            
            # convert price to in-game values
            season_history['£S'] = (season_history['£S'] / 10)
            season_history['£E'] = (season_history['£E'] / 10)


        return gameweek_history, season_history


    def get_fixtures(self):
        '''Get all fixtures'''

        # get all data from fpl api
        data = requests.get(BASE_URL+'fixtures/').json()

        fixtures = pd.DataFrame(
            data
        )
        # .drop(
        #     ['code', 'played', 'form', 'win', 'draw', 'loss', 'points',
        #      'position', 'team_division', 'unavailable', 'pulse_id'],
        #     axis=1
        # ).rename(columns={
        #     'id': 'team_id',
        #     'short_name': 'team',
        #     'name': 'team_name_long'}
        # ).set_index(
        #     'team_id'
        # )

        return fixtures





class FplManagerData:
    
    def __init__(self, manager_id, gw):
        '''Loads all manager data from API'''

        # get all data from fpl api
        info = requests.get(f'{BASE_URL}entry/{manager_id}/').json()
        history = requests.get(f'{BASE_URL}entry/{manager_id}/history/').json()

        # squad from previous gameweek
        picks = pd.DataFrame(
            requests.get(
                f'{BASE_URL}entry/{manager_id}/event/{gw}/picks/'
            ).json()['picks']
        ).rename(columns={
            'element': 'player_id'}
        ).drop(
            'position', axis=1
        )

        self.picks = picks

