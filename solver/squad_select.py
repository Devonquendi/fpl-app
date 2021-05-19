import os
import pandas as pd
import sasoptpy as so
from subprocess import Popen, DEVNULL
from datasets import FplApiData


class SelectionModel:

    def __init__(self, team_id, next_gw, forecasts_file):

        # API data
        api_data = FplApiData(team_id, next_gw-1)
        # players
        self.players = api_data.players
        # position IDs, names and squad limits
        self.positions = api_data.positions
        # team IDs and names
        self.teams = api_data.teams
        # current squad
        self.current_squad = api_data.current_squad
        # in the bank
        self.bank = api_data.bank
        # upcoming gameweek
        self.next_gw = next_gw
        # Review data
        self.forecasts = api_data.make_opt_df(forecasts_file)
        

    def create_model(self, budget=100, num_weeks=1):
        
        # ToDo: try using pandas index instead of lists
        player_list = self.forecasts.index.tolist()
        position_list = self.positions.index.tolist()
        team_list = self.teams.index.tolist()

        model_name = f'gw{self.next_gw}_{budget}budget_{num_weeks}weeks'
        model = so.Model(model_name)

        # Variables
        squad   = model.add_variables(player_list,name='squad',
                                      vartype=so.binary)
        lineup  = model.add_variables(player_list, name='lineup', 
                                      vartype=so.binary)
        captain = model.add_variables(player_list, name='captain', 
                                      vartype=so.binary)
        vicecap = model.add_variables(player_list, name='vicecap', 
                                      vartype=so.binary)

        # Constraints
        # 15 players in squad
        squad_count = so.expr_sum(squad[p] for p in player_list)
        model.add_constraint(squad_count == 15, name='squad_count')
        # 11 players in starting lineup
        model.add_constraint(so.expr_sum(lineup[p] for p in player_list) == 11,
                             name='lineup_count')
        # 1 captain
        model.add_constraint(so.expr_sum(captain[p] for p in player_list) == 1,
                             name='captain_count')
        # 1 vice-captain
        model.add_constraint(so.expr_sum(vicecap[p] for p in player_list) == 1,
                             name='vicecap_count')
        # players in starting lineup must also be in squad
        model.add_constraints((lineup[p] <= squad[p] for p in player_list),
                              name='lineup_squad_rel')
        # captain must come from within squad
        model.add_constraints((captain[p] <= lineup[p] for p in player_list),
                              name='captain_lineup_rel')
        # vice-captain must come from within squad
        model.add_constraints((vicecap[p] <= lineup[p] for p in player_list),
                              name='vicecap_lineup_rel')
        # captain and vice-captain can't be same person
        model.add_constraints((captain[p] + vicecap[p] <= 1 for p in player_list),
                              name='cap_vc_rel')
        # count of each player per position in starting lineup
        lineup_type_count = {
            t: so.expr_sum(lineup[p] for p in player_list
                           if self.forecasts.loc[p, 'position_id'] == t)
            for t in position_list}
        # count of all players in squad must be at least 'squad_min_play'
        # and no more than 'squad_max_play' for each position type 
        model.add_constraints(
            (lineup_type_count[t] == [self.positions.loc[t, 'squad_min_play'],
                                      self.positions.loc[t, 'squad_max_play']]
             for t in position_list),
            name='valid_formation')
        # count of each player per position in squad
        squad_type_count = {
            t: so.expr_sum(squad[p] for p in player_list
                           if self.forecasts.loc[p, 'position_id'] == t)
            for t in position_list}
        # count of all players in squad must be equal to 'squad_select'
        # for each position type 
        model.add_constraints(
            (squad_type_count[t] == self.positions.loc[t, 'squad_select']
             for t in position_list),
            name='valid_squad')
        # total value of squad cannot exceed budget
        price = so.expr_sum(
            self.forecasts.loc[p, 'bv'] * squad[p] for p in player_list)
        model.add_constraint(price <= budget, name='budget_limit')
        # no more than 3 players per team
        model.add_constraints(
            (
                so.expr_sum(squad[p] for p in player_list
                            if self.forecasts.loc[p, 'team_id'] == t)
                <= 3 for t in team_list),
            name='team_limit'
        )
        # sum of starting 11 players, plus double captain score
        # and upweight vice-captain
        total_points = so.expr_sum(self.forecasts.loc[p, f'{self.next_gw}_pts']
                                   * (lineup[p] + captain[p] + 0.1 * vicecap[p])
                                   for p in player_list)

        # Objective
        model.set_objective(-total_points, sense='N', name='total_xp')
        model.export_mps(f'{model_name}.mps')
        command = f'cbc {model_name}.mps solve solu {model_name}.txt'

        Popen(command, shell=False, stdout=DEVNULL).wait()
        for v in model.get_variables():
            v.set_value(0)
        with open(f'{model_name}.txt', 'r') as f:
            for line in f:
                if 'objective value' in line:
                    continue
                words = line.split()
                var = model.get_variable(words[1])
                var.set_value(float(words[2]))

        picks = []
        for p in player_list:
            if squad[p].get_value() > 0.5:
                lp = self.forecasts.loc[p]
                is_captain = 1 if captain[p].get_value() > 0.5 else 0
                is_lineup = 1 if lineup[p].get_value() > 0.5 else 0
                is_vice = 1 if vicecap[p].get_value() > 0.5 else 0
                position = self.positions.loc[lp['position_id'], 'position_name']
                team = self.teams.loc[lp['team_id'], 'team_name']
                picks.append([lp['web_name'], lp['position_id'], position, team,
                              lp['bv'], round(lp[f'{self.next_gw}_pts'], 2),
                              is_lineup, is_captain, is_vice])

        picks_df = pd.DataFrame(
            picks,
            columns=['Name', 'Pos_id', 'Pos', 'Team', 'Price', 'xP', 'lineup',
                     'captain', 'vicecaptain']
        ).sort_values(by=['lineup', 'Pos_id', 'xP'], ascending=[False, True, True])
        
        total_xp = so.expr_sum((lineup[p] + captain[p])
                                * self.forecasts.loc[p, f'{self.next_gw}_pts']
                                for p in player_list).get_value()

        print(f'Total expected value for budget {budget}: {total_xp}')
        print(picks_df)

        os.remove(f'{model_name}.txt')

        return picks_df


if __name__ == '__main__':

    model = SelectionModel(team_id=384484, next_gw=37,
        forecasts_file=os.path.join('..', 'data', 'fplreview', 'gw37-38.csv'))

    print(model.players)
    print(model.positions)
    print(model.teams)
    print(model.forecasts)

    picks = model.create_model()
