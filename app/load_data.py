import pandas as pd
import streamlit as st


data_url = 'https://raw.githubusercontent.com/datahounds/fantasy-premier-league/master/data/2022-23/'


# @st.cache
class FplData:
    
    def __init__(self):
        '''Loads all saved FPL API data from GitHub'''

        df = pd.read_csv(data_url + 'players.csv')
        positions = pd.read_csv(data_url + 'positions.csv')
        teams = pd.read_csv(data_url + 'teams.csv')
        # history = pd.read_csv(data_url + 'gameweek_history.csv')

        # exclude who haven't played enough minutes
        df = df[df['minutes'] > 270]
        df = df.merge(teams, on='team_id').merge(positions, on='position_id')

        # infer the games played column from points / points_per_game
        df['GP'] = df['total_points'].divide(df['points_per_game']).round(0).astype('int')  # / df['points_per_game']
        
        # drop columns we are not interested in
        df = df[
            ['player_id', 'web_name', 'short_name', 'position_name', 'now_cost', 'total_points',
             'GP', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'goals_conceded',
             'own_goals', 'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards',
             'saves', 'bonus', 'bps', 'influence', 'creativity', 'threat', 'ict_index']
        ].set_index('player_id')

        df.columns = ['name', 'team', 'pos', '£', 'Pts', 'GP', 'MP', 'GS', 'A', 'CS', 'GC', 'OG', 'PS',
                      'PM', 'YC', 'RC', 'S', 'B', 'BPS', 'I', 'C', 'T', 'II']

        df['£'] = df['£'] / 10

        score_cols = ['Pts', 'GS', 'A', 'CS', 'GC', 'OG', 'PS', 'PM', 'YC', 'RC', 'S', 'B', 'BPS',
            'I', 'C', 'T', 'II']
        # add "per 90" metrics
        df_90 = df.copy()
        df_90[score_cols] = df_90[score_cols].divide(df_90['MP'] / 90, axis=0)
        # add "per game" metrics
        df_gp = df.copy()
        df_gp[score_cols] = df_gp[score_cols].divide(df_gp['GP'], axis=0)
        # df[[c + '/GP' for c in score_cols]] = df[score_cols].divide(df['GP'], axis=0)

        # info_cols = ['name', 'team', 'pos', '£', 'GP', 'MP']
        # score_90_cols = [c + '/90' for c in score_cols]
        # score_gp_cols = [c + '/GP' for c in score_cols]

        # df_total = df[info_cols + score_cols].round(1).sort_values('Pts', ascending=False)
        # df_90 = df_90[info_cols + score_90_cols].sort_values('Pts/90', ascending=False)
        # df_gp = df[info_cols + score_gp_cols].sort_values('Pts/GP', ascending=False)

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

        # self.history = history
        self.teams = teams
        self.positions = positions
        self.df_total = df.round(1).sort_values('Pts', ascending=False)
        self.df_90 = df_90.round(1).sort_values('Pts', ascending=False)
        self.df_gp = df_gp.round(1).sort_values('Pts', ascending=False)


