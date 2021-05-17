import os
import pandas as pd
import sasoptpy as so
from subprocess import Popen, DEVNULL
from datasets import FplApiData


class SelectionModel:

    def __init__(self, forecasts_file):

        self.positions = FplApiData().transform_positions()
        self.df = pd.read_csv(forecasts_file)
        

    def create_model(self, budget=100, num_weeks=1):
        
        player_list = self.df.index.tolist()
        position_list = self.positions.index.tolist()
        team_list = self.df['Team'].unique().tolist()
        next_gw = int(self.df.keys()[5].split('_')[0])

        model_name = f'gw{next_gw}_{budget}budget_{num_weeks}weeks'
        model = so.Model(model_name)

        # Variables
        squad = model.add_variables(player_list, name='squad', vartype=so.binary)
        lineup = model.add_variables(player_list, name='lineup', vartype=so.binary)
        captain = model.add_variables(player_list, name='captain', vartype=so.binary)
        vicecap = model.add_variables(player_list, name='vicecap', vartype=so.binary)

        # Constraints
        # 15 players in squad
        squad_count = so.expr_sum(squad[p] for p in player_list)
        model.add_constraint(squad_count == 15, name='squad_count')
        # 11 players in starting lineup
        model.add_constraint(
            so.expr_sum(lineup[p] for p in player_list) == 11, name='lineup_count'
        )
        # 1 captain
        model.add_constraint(
            so.expr_sum(captain[p] for p in player_list) == 1, name='captain_count'
        )
        # 1 vice-captain
        model.add_constraint(
            so.expr_sum(vicecap[p] for p in player_list) == 1, name='vicecap_count'
        )
        # players in starting lineup must also be in squad
        model.add_constraints(
            (lineup[p] <= squad[p] for p in player_list), name='lineup_squad_rel'
        )
        # captain must come from within squad
        model.add_constraints(
            (captain[p] <= lineup[p] for p in player_list), name='captain_lineup_rel'
        )
        # vice-captain must come from within squad
        model.add_constraints(
            (vicecap[p] <= lineup[p] for p in player_list), name='vicecap_lineup_rel'
        )
        # captain and vice-captain can't be same person
        model.add_constraints(
            (captain[p] + vicecap[p] <= 1 for p in player_list), name='cap_vc_rel'
        )

        # count of each player per position in starting lineup
        lineup_type_count = {
            t: so.expr_sum(
                lineup[p] for p in player_list if self.df.loc[p, 'Pos'] == t
            ) for t in self.positions
        }

        # count of all players in squad must be at least 'squad_min_play'
        # and no more than 'squad_max_play' for each position type 
        model.add_constraints(
            (lineup_type_count[t] == [
                self.positions.loc[t, 'squad_min_play'],
                self.positions.loc[t, 'squad_max_play']
            ] for t in position_list),
            name='valid_formation'
        )

        # count of each player per position in squad
        squad_type_count = {
            t: so.expr_sum(
                squad[p] for p in player_list if self.df.loc[p, 'Pos'] == t
            ) for t in position_list
        }

        # count of all players in squad must be equal to 'squad_select'
        # for each position type 
        model.add_constraints(
            (squad_type_count[t] == self.positions.loc[t, 'squad_select'] for t in position_list),
            name='valid_squad'
        )

        # total value of squad cannot exceed budget
        price = so.expr_sum(self.df.loc[p, 'BV'] * squad[p] for p in player_list)
        model.add_constraint(price <= budget, name='budget_limit')

        # no more than 3 players per team
        model.add_constraints(
            (so.expr_sum(
                squad[p] for p in player_list if self.df.loc[p, 'Team'] == t
            ) <= 3 for t in team_list),
            name='team_limit'
        )

        # sum of starting 11 players, plus double captain score and upweight vice-captain
        total_points = so.expr_sum(
            self.df.loc[p, 'Pts'] * (lineup[p] + captain[p] + 0.1 * vicecap[p]) for p in player_list
        )

        model.set_objective(-total_points, sense='N', name='total_xp')
        model.export_mps(f'single_period_{budget}.mps')
        command = f'cbc single_period_{budget}.mps solve solu solution_sp_{budget}.txt'

        Popen(command, shell=False, stdout=DEVNULL).wait()
        for v in model.get_variables():
            v.set_value(0)
        with open(f'solution_sp_{budget}.txt', 'r') as f:
            for line in f:
                if 'objective value' in line:
                    continue
                words = line.split()
                var = model.get_variable(words[1])
                var.set_value(float(words[2]))

        picks = []
        for p in player_list:
            if squad[p].get_value() > 0.5:
                lp = self.df.loc[p]
                is_captain = 1 if captain[p].get_value() > 0.5 else 0
                is_lineup = 1 if lineup[p].get_value() > 0.5 else 0
                is_vice = 1 if vicecap[p].get_value() > 0.5 else 0
                picks.append([
                    lp['Name'], lp['Pos'], lp['Team'], lp['BV'], round(lp[f'{next_gw}_Pts'], 2), is_lineup, is_captain, is_vice
                ])

        picks_df = pd.DataFrame(picks, columns=['Name', 'Pos', 'Team', 'Price', 'xP', 'lineup', 'captain', 'vicecaptain']).sort_values(by=['lineup', 'Pos', 'xP'], ascending=[False, True, True])
        total_xp = so.expr_sum((lineup[p] + captain[p]) * self.df.loc[p, f'{next_gw}_Pts'] for p in player_list).get_value()

        print(f'Total expected value for budget {budget}: {total_xp}')

        return {'model': model, 'picks': picks_df, 'total_xp': total_xp}


if __name__ == '__main__':

    model = SelectionModel(os.path.join('..', 'data', 'fplreview', 'gw37-38.csv'))

    model.create_model()


