import pandas as pd
import sasoptpy as so
import os
from argparse import ArgumentParser
from subprocess import Popen, DEVNULL
from datasets import FplApiData


class SelectionModel:

    def __init__(self, team_id, gw, forecasts_file):

        '''Downloads data from fpl api 
           and combines with input from fplreview.com'''

        # API data
        api_data = FplApiData(team_id=team_id, gw=gw-1)
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
        self.gw = gw
        # Review data
        self.forecasts = api_data.make_opt_df(forecasts_file)
        

    def solve_optimal_squad(self, budget=100):
        
        players = self.forecasts.index
        positions = self.positions.index
        teams = self.teams.index

        model_name = f'gw{self.gw}_{budget}budget'
        model = so.Model(model_name)

        # Variables
        squad   = model.add_variables(players,name='squad',
                                      vartype=so.binary)
        lineup  = model.add_variables(players, name='lineup', 
                                      vartype=so.binary)
        captain = model.add_variables(players, name='captain', 
                                      vartype=so.binary)
        vicecap = model.add_variables(players, name='vicecap', 
                                      vartype=so.binary)

        # Constraints
        # 15 players in squad
        squad_count = so.expr_sum(squad[p] for p in players)
        model.add_constraint(squad_count == 15, name='squad_count')
        # 11 players in starting lineup
        model.add_constraint(so.expr_sum(lineup[p] for p in players) == 11,
                             name='lineup_count')
        # 1 captain
        model.add_constraint(so.expr_sum(captain[p] for p in players) == 1,
                             name='captain_count')
        # 1 vice-captain
        model.add_constraint(so.expr_sum(vicecap[p] for p in players) == 1,
                             name='vicecap_count')
        # players in starting lineup must also be in squad
        model.add_constraints((lineup[p] <= squad[p] for p in players),
                              name='lineup_squad_rel')
        # captain must come from within squad
        model.add_constraints((captain[p] <= lineup[p] for p in players),
                              name='captain_lineup_rel')
        # vice-captain must come from within squad
        model.add_constraints((vicecap[p] <= lineup[p] for p in players),
                              name='vicecap_lineup_rel')
        # captain and vice-captain can't be same person
        model.add_constraints((captain[p] + vicecap[p] <= 1 for p in players),
                              name='cap_vc_rel')
        # count of each player per position in starting lineup
        lineup_type_count = {
            t: so.expr_sum(lineup[p] for p in players
                           if self.forecasts.loc[p, 'position_id'] == t)
            for t in positions}
        # count of all players in lineup must be at least 'squad_min_play'
        # and no more than 'squad_max_play' for each position type 
        model.add_constraints(
            (lineup_type_count[t] == [self.positions.loc[t, 'squad_min_play'],
                                      self.positions.loc[t, 'squad_max_play']]
             for t in positions),
            name='valid_formation')
        # count of each player per position in squad
        squad_type_count = {
            t: so.expr_sum(squad[p] for p in players
                           if self.forecasts.loc[p, 'position_id'] == t)
            for t in positions}
        # count of all players in squad must be equal to 'squad_select'
        # for each position type 
        model.add_constraints(
            (squad_type_count[t] == self.positions.loc[t, 'squad_select']
             for t in positions),
            name='valid_squad')
        # total value of squad cannot exceed budget
        price = so.expr_sum(
            self.forecasts.loc[p, 'bv'] * squad[p] for p in players)
        model.add_constraint(price <= budget, name='budget_limit')
        # no more than 3 players per team
        model.add_constraints(
            (
                so.expr_sum(squad[p] for p in players
                            if self.forecasts.loc[p, 'team_id'] == t)
                <= 3 for t in teams),
            name='team_limit'
        )
        # sum of starting 11 players, plus double captain score
        # and upweight vice-captain
        total_points = so.expr_sum(self.forecasts.loc[p, f'{self.gw}_pts']
                                   * (lineup[p] + captain[p] + 0.1 * vicecap[p])
                                   for p in players)

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
        for p in players:
            if squad[p].get_value() > .5:
                lp = self.forecasts.loc[p]
                is_captain = 1 if captain[p].get_value() > .5 else 0
                is_lineup = 1 if lineup[p].get_value() > .5 else 0
                is_vice = 1 if vicecap[p].get_value() > .5 else 0
                position = self.positions.loc[lp['position_id'], 'position_name']
                team = self.teams.loc[lp['team_id'], 'team_name']
                picks.append([lp['web_name'], lp['position_id'], position, team,
                              lp['bv'], round(lp[f'{self.gw}_pts'], 2),
                              is_lineup, is_captain, is_vice])

        picks_df = pd.DataFrame(
            picks,
            columns=['Name', 'Pos_id', 'Pos', 'Team', 'Price', 'xP', 'lineup',
                     'captain', 'vicecaptain']
        ).sort_values(by=['lineup', 'Pos_id', 'xP'], ascending=[False, True, True])
        
        total_xp = so.expr_sum((lineup[p] + captain[p])
                                * self.forecasts.loc[p, f'{self.gw}_pts']
                                for p in players).get_value()

        print(f'Total expected value for budget {budget:.1f}: {total_xp:.2f}')

        os.remove(f'{model_name}.mps')
        os.remove(f'{model_name}.txt')

        return picks_df


    def solve_multi_week(self, ft, horizon, decay_base=1.0):
        
        # ToDo: absorb optimal squad method into this one
        #       compare your own team outcomes with the optimal squad
        #       useful for deciding when to wildcard
        # ToDo: add parameter for helping to decide on when to use bench boost
        # ToDo: add constraint description comments
        '''
        Solves multi-objective FPL problem with transfers
        Parameters
        ----------
        ft: integer
            Number of available free transfers (currently)
        horizon: integer
            Number of weeks to consider in optimization
        decay_base: float
            Base for the decay function, default of 1 means no decay
        '''

        # Data
        players = self.forecasts.index
        positions = self.positions.index
        teams = self.teams.index
        current_squad = self.current_squad['player_id'].tolist()
        itb = self.bank
        gameweeks = list(range(self.gw, self.gw+horizon))
        all_gw = [self.gw-1] + gameweeks

        # Model
        model_name = f'w{self.gw}_h{horizon}_d{decay_base}'
        model = so.Model(model_name)

        # Variables
        squad = model.add_variables(
            players, all_gw, name='squad', vartype=so.binary)
        lineup = model.add_variables(
            players, gameweeks, name='lineup', vartype=so.binary)
        captain = model.add_variables(
            players, gameweeks, name='captain', vartype=so.binary)
        vicecap = model.add_variables(
            players, gameweeks, name='vicecap', vartype=so.binary)
        transfer_in = model.add_variables(
            players, gameweeks, name='transfer_in', vartype=so.binary)
        transfer_out = model.add_variables(
            players, gameweeks, name='transfer_out', vartype=so.binary)
        in_the_bank = model.add_variables(
            all_gw, name='itb', vartype=so.continuous, lb=0)
        free_transfers = model.add_variables(
            all_gw, name='ft', vartype=so.integer, lb=1, ub=2)
        penalized_transfers = model.add_variables(
            gameweeks, name='pt', vartype=so.integer, lb=0)
        # artificial binary variable to handle transfer logic
        aux = model.add_variables(
            gameweeks, name='aux', vartype=so.binary)
        
        # Dictionaries
        # sell prices of all players
        sell_price = self.forecasts['sv'].to_dict()
        # buy prices of all players
        buy_price = self.forecasts['bv'].to_dict()
        # total bank earned from selling players across gameweeks
        sold_amount = {w: so.expr_sum(sell_price[p] * transfer_out[p,w]
                                    for p in players)
                    for w in gameweeks}
        # total bank spent on buying players across gameweeks
        bought_amount = {w: so.expr_sum(buy_price[p] * transfer_in[p,w]
                                        for p in players)
                        for w in gameweeks}
        # player weekly forecast points
        points_player_week = {(p,w): self.forecasts.loc[p, f'{w}_pts']
                            for p in players for w in gameweeks}
        # number of transfers made each week
        number_of_transfers = {w: so.expr_sum(transfer_out[p,w] for p in players)
                            for w in gameweeks}
        # assume one transfer was made last week ?? why ??
        number_of_transfers[self.gw-1] = 1
        transfer_diff = {w: number_of_transfers[w] - free_transfers[w]
                        for w in gameweeks}

        # Initial conditions
        # set squad = 1 for all players currently in squad at previous GW deadline
        model.add_constraints(
            (squad[p, self.gw-1] == 1 for p in current_squad),
            name='initial_squad_players')
        # set squad = 0 for all other players
        model.add_constraints(
            (squad[p, self.gw-1] == 0 for p in players if p not in current_squad),
            name='initial_squad_others')
        # add current bank value
        model.add_constraint(in_the_bank[self.gw-1] == itb, name='initial_itb')
        # add current free transfers
        model.add_constraint(free_transfers[self.gw-1] == ft, name='initial_ft')

        # Constraints (per week)
        # 15 players in squad
        squad_count = {
            w: so.expr_sum(squad[p, w] for p in players)
            for w in gameweeks}
        model.add_constraints(
            (squad_count[w] == 15 for w in gameweeks), name='squad_count')
        # 11 players in starting lineup
        model.add_constraints(
            (so.expr_sum(lineup[p,w] for p in players) == 11 for w in gameweeks), 
            name='lineup_count')
        # 1 captain
        model.add_constraints(
            (so.expr_sum(captain[p,w] for p in players) == 1 for w in gameweeks), 
            name='captain_count')
        # 1 vice-captain
        model.add_constraints(
            (so.expr_sum(vicecap[p,w] for p in players) == 1 for w in gameweeks), 
            name='vicecap_count')
        # players in starting lineup must also be in squad
        model.add_constraints(
            (lineup[p,w] <= squad[p,w] for p in players for w in gameweeks), 
            name='lineup_squad_rel')
        # captain must come from within squad
        model.add_constraints(
            (captain[p,w] <= lineup[p,w] for p in players for w in gameweeks), 
            name='captain_lineup_rel')
        # vice-captain must come from within squad
        model.add_constraints(
            (vicecap[p,w] <= lineup[p,w] for p in players for w in gameweeks), 
            name='vicecap_lineup_rel')
        # captain and vice-captain can't be same person
        model.add_constraints(
            (captain[p,w] + vicecap[p,w] <= 1 for p in players for w in gameweeks), 
            name='cap_vc_rel')
        # count of each player per position in starting lineup
        lineup_type_count = {
            (t,w): so.expr_sum(lineup[p,w] for p in players
                               if self.forecasts.loc[p, 'position_id'] == t)
            for t in positions for w in gameweeks}
        # count of all players in lineup must be at least 'squad_min_play'
        # and no more than 'squad_max_play' for each position type
        model.add_constraints(
            (
                lineup_type_count[t,w] == [
                    self.positions.loc[t, 'squad_min_play'],
                    self.positions.loc[t, 'squad_max_play']] 
                for t in positions for w in gameweeks),
            name='valid_formation')
        # count of each player per position in squad
        squad_type_count = {
            (t,w): so.expr_sum(squad[p,w] for p in players
                               if self.forecasts.loc[p, 'position_id'] == t)
            for t in positions for w in gameweeks}
        # count of all players in squad must be equal to 'squad_select'
        # for each position type
        model.add_constraints(
            (
                squad_type_count[t,w] == self.positions.loc[t, 'squad_select']
                for t in positions for w in gameweeks),
            name='valid_squad')
        # no more than 3 players per team
        model.add_constraints(
            (
                so.expr_sum(squad[p,w] for p in players
                            if self.forecasts.loc[p, 'team_id'] == t)
                <= 3 for t in teams for w in gameweeks),
            name='team_limit')
        # Transfer constraints
        # squad is equal to squad from previous week, minus transfers out, plus in
        model.add_constraints(
            (
                squad[p,w] == squad[p,w-1] + transfer_in[p,w] - transfer_out[p,w]
                for p in players for w in gameweeks),
            name='squad_transfer_rel')
        # handles running bank balance (assumes no changes in player values)
        model.add_constraints(
            (
                in_the_bank[w] == in_the_bank[w-1] + sold_amount[w] - bought_amount[w]
                for w in gameweeks),
            name='cont_budget')
        # Free transfer constraints
        # 1 free transfer per week
        model.add_constraints(
            (free_transfers[w] == aux[w] + 1 for w in gameweeks),
            name='aux_ft_rel')
        # no more than 2 free transfers per week
        model.add_constraints(
            (
                free_transfers[w-1] - number_of_transfers[w-1] <= 2 * aux[w]
                for w in gameweeks),
            name='force_aux_1')
        # cannot make more than 14 penalized transfers in a week
        model.add_constraints(
            (
                free_transfers[w-1] - number_of_transfers[w-1] >= aux[w]
                + (-14)*(1-aux[w]) 
                for w in gameweeks),
            name='force_aux_2')
        # not sure what this does ??
        model.add_constraints(
            (penalized_transfers[w] >= transfer_diff[w] for w in gameweeks),
            name='pen_transfer_rel')

        # Objectives
        # sum of starting 11 players, plus double captain score 
        # and upweight vice-captain
        gw_xp = {
            w: so.expr_sum(points_player_week[p,w]
                        * (lineup[p,w] + captain[p,w]
                        + 0.1*vicecap[p,w]) for p in players)
            for w in gameweeks}
        # subtract transfer costs
        gw_total = {w: gw_xp[w] - 4 * penalized_transfers[w] for w in gameweeks}
        total_xp = so.expr_sum(
            gw_total[w] * pow(decay_base, w-self.gw) for w in gameweeks)
        model.set_objective(-total_xp, sense='N', name='total_xp')

        # Solve
        model.export_mps(f'{model_name}.mps')
        command = f'cbc {model_name}.mps solve solu {model_name}.txt'
        process = Popen(command, stdout=DEVNULL, shell=False) # DEVNULL: nologs
        process.wait()

        # Parsing
        with open(f'{model_name}.txt', 'r') as f:
            for line in f:
                if 'objective value' in line:
                    continue
                words = line.split()
                var = model.get_variable(words[1])
                var.set_value(float(words[2]))

        # DataFrame generation
        picks = []
        for w in gameweeks:
            for p in players:
                if squad[p,w].get_value() + transfer_out[p,w].get_value() > .5:
                    lp = self.forecasts.loc[p]
                    is_captain = 1 if captain[p,w].get_value() > .5 else 0
                    is_lineup = 1 if lineup[p,w].get_value() > .5 else 0
                    is_vice = 1 if vicecap[p,w].get_value() > .5 else 0
                    is_transfer_in = 1 if transfer_in[p,w].get_value() > .5 else 0
                    is_transfer_out = 1 if transfer_out[p,w].get_value() > .5 else 0
                    position = self.positions.loc[lp['position_id'], 'position_name']
                    team = self.teams.loc[lp['team_id'], 'team_name']
                    picks.append([
                        w, lp['web_name'], lp['position_id'], position, team, 
                        buy_price[p], sell_price[p], round(points_player_week[p,w],2),
                        is_lineup, is_captain, is_vice, is_transfer_in, is_transfer_out
                    ])

        picks_df = pd.DataFrame(
            picks,
            columns=['GW', 'Name', 'Pos_id', 'Pos', 'Team', 'BV', 'SV', 'xP',
                    'lineup', 'captain', 'vicecaptain', 'transfer_in', 'transfer_out']
        ).sort_values(
            by=['GW', 'lineup', 'Pos_id', 'xP'],
            ascending=[True, False, True, True])
        total_xp = so.expr_sum(
            (lineup[p,w] + captain[p,w]) * points_player_week[p,w]
            for p in players for w in gameweeks
        ).get_value()


        print('SUMMARY OF ACTIONS', '-----------', sep='\n')
        for w in gameweeks:
            print(f'GW {w}:')
            print(f'ITB {in_the_bank[w].get_value()}:',
                  f'FT={free_transfers[w].get_value()}',
                  f'PT={penalized_transfers[w].get_value()}')
            for p in players:
                if transfer_in[p,w].get_value() > .5:
                    print(f'   Buy {p} - {self.forecasts["web_name"][p]}')
                if transfer_out[p,w].get_value() > .5:
                    print(f'   Sell {p} - {self.forecasts["web_name"][p]}')
        print(f'\nTotal expected value: {total_xp:.2f} ({total_xp/horizon:.2f} / week)')

        os.remove(f'{model_name}.mps')
        os.remove(f'{model_name}.txt')

        return picks_df


if __name__ == '__main__':

    parser = ArgumentParser(
        description='Optimises squad selection for given time horizon')
    parser.add_argument('-t', '--team_id', type=str, default=269471,
                        help='unique ID of FPL manager')
    parser.add_argument('-w', '--gameweek', type=int, required=True,
                        help='upcoming gameweek number')
    parser.add_argument('-f', '--forecasts', type=str, required=True,
                        help='path to FPLreview forecasts file')
    parser.add_argument('-ft', '--free_transfers', type=int, default=1,
                        help='number of free transfers for upcoming week')
    parser.add_argument('-hz', '--horizon', type=int, default=2,
                        help='number of weeks to look forward')
    parser.add_argument('-d', '--decay', type=float, default=1.0,
                        help='number of weeks to look forward')

    args = parser.parse_args()

    # make sure using correct separators for path names
    forecasts = args.forecasts.replace('/', os.sep)

    model = SelectionModel(team_id=args.team_id, gw=args.gameweek,
        forecasts_file=forecasts)

    print('OPTIMIZING ACTION PLAN')
    picks = model.solve_multi_week(
        ft=args.free_transfers, horizon=args.horizon, decay_base=args.decay)
    print('\nSQUAD PICKS:')
    print(picks)
    print('\n\nFINDING OPTIMAL SQUAD FOR UPCOMING WEEK')
    optimal_squad = model.solve_optimal_squad()
    print('\nOPTIMAL SQUAD:')
    print(optimal_squad)
