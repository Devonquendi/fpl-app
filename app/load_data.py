import pandas as pd
import streamlit as st


data_url = 'https://raw.githubusercontent.com/datahounds/fantasy-premier-league/master/data/2021-22/'

# @st.cache
class FplData:
    
    # @st.cache
    def __init__(self):
        '''Loads all saved FPL API data from GitHub'''

        players = pd.read_csv(data_url + 'players.csv')
        positions = pd.read_csv(data_url + 'positions.csv')
        teams = pd.read_csv(data_url + 'teams.csv')
        history = pd.read_csv(data_url + 'gameweek_history.csv')

        players = players.merge(teams, on='team_id').merge(positions, on='position_id')[
            ['player_id', 'web_name', 'short_name', 'position_name', 'now_cost']].set_index('player_id')

        players.columns = ['name', 'team', 'pos', '£']
        players['£'] = players['£'] = players['£'] / 10

        history = history.merge(teams, left_on='opponent_team', right_on='team_id')

        # calculate opponent strength based on whether match was home or away
        history['vs_ovr'] = (history['was_home'] * history['strength_overall_home']) + (~history['was_home'] * history['strength_overall_away'])
        history['vs_att'] = (history['was_home'] * history['strength_attack_home']) + (~history['was_home'] * history['strength_attack_away'])
        history['vs_def'] = (history['was_home'] * history['strength_defence_home']) + (~history['was_home'] * history['strength_defence_away'])
        history['vs'] = history.apply(lambda s: s['short_name'] + ' (H)' if s['was_home'] else s['short_name'] + ' (A)', axis=1)

        history = history[['player_id', 'round', 'vs', 'strength', 'vs_ovr', 'vs_att', 'vs_def',
                'total_points', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'goals_conceded',
                'own_goals', 'penalties_saved', 'bonus', 'bps', 'influence', 'creativity', 'threat',
                'ict_index', 'value', 'selected', 'transfers_balance']]

        history.columns = ['player_id', 'GW', 'vs', 'vs_strength', 'vs_ovr', 'vs_att', 'vs_def', 'Pts', 'MP',
                    'GS', 'A', 'CS', 'GC', 'OG', 'PS', 'B', 'BPS', 'I', 'C', 'T', 'II', '£', 'TSB', 'NT']

        # convert price to in-game values
        history['£'] = history['£'] / 10

        # create game_played column
        history['GP'] = history['MP'] > 0

        self.players = players
        self.history = history

    @st.cache
    def get_summary(self):
        '''Create dataframe with player season summaries'''

        # aggregate data into summary table
        df = self.history.drop(
            ['GW', 'vs', 'vs_strength', 'vs_ovr', 'vs_att', 'vs_def', '£', 'TSB'], axis=1)
        df = self.players.merge(
            df.groupby('player_id').sum(), on='player_id')

        # exclude players with too few minutes
        df = df[df['MP']>270]

        # add "per 90" metrics
        df[['Pts/90', 'I/90', 'C/90', 'T/90', 'II/90']] = df[['Pts', 'I', 'C', 'T', 'II']].divide(df['MP'] / 90, axis=0)
        # add "per game" metrics
        df[['Pts/GP', 'I/GP', 'C/GP', 'T/GP', 'II/GP']] = df[['Pts', 'I', 'C', 'T', 'II']].divide(df['GP'], axis=0)

        df.sort_values('Pts/GP', ascending=False, inplace=True)

        return df
