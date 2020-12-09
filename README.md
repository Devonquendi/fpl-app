# fantasy-premier-league
Data-driven decision making tool for [Fantasy Premier League](https://fantasy.premierleague.com/)

## List of useful links:
  * [Fantasy Premier League Value Analysis Python Tutorial using the FPL API](https://towardsdatascience.com/fantasy-premier-league-value-analysis-python-tutorial-using-the-fpl-api-8031edfe9910)
  * [Reddit thread](https://www.reddit.com/r/FantasyPL/comments/c64rrx/fpl_api_url_has_been_changed/)

## Getting started

Get a list of the fields availabe at the `bootstrap-static` endpoint:
```python
import requests, json
import pandas as pd

fpl_url = 'https://fantasy.premierleague.com/api/'

r = requests.get(fpl_url + 'bootstrap-static/')
print(r.json().keys())
```
`Out:`
```bash
>> dict_keys(['events', 'game_settings', 'phases', 'teams', 'total_players', 'elements', 'element_stats', 'element_types'])

```
The three main fields of interest are `elements`, `element_types` and `teams`

### Player data (`elements`)
The `elements` field contains data for every active player in the current season.

```python
r = requests.get(fpl_url + 'bootstrap-static/')

players = pd.json_normalize(
    r.json()['elements']
)
```

|column|dtype|description|
|---|---|---|
|chance_of_playing_next_round|||
|chance_of_playing_this_round|||
|code|||
|cost_change_event|||
|cost_change_event_fall|||
|cost_change_start|||
|cost_change_start_fall|||
|dreamteam_count|||
|element_type|||
|ep_next|||
|ep_this|||
|event_points|||
|first_name|||
|form|||
|id|||
|in_dreamteam|||
|news|||
|news_added|||
|now_cost|||
|photo|||
|points_per_game|||
|second_name|||
|selected_by_percent|||
|special|||
|squad_number|||
|status|||
|team|||
|team_code|||
|total_points|||
|transfers_in|||
|transfers_in_event|||
|transfers_out|||
|transfers_out_event|||
|value_form|||
|value_season|||
|web_name|||
|minutes|||
|goals_scored|||
|assists|||
|clean_sheets|||
|goals_conceded|||
|own_goals|||
|penalties_saved|||
|penalties_missed|||
|yellow_cards|||
|red_cards|||
|saves|||
|bonus|||
|bps|||
|influence|||
|creativity|||
|threat|||
|ict_index|||
|influence_rank|||
|influence_rank_type|||
|creativity_rank|||
|creativity_rank_type|||
|threat_rank|||
|threat_rank_type|||
|ict_index_rank|||
|ict_index_rank_type|||
|corners_and_indirect_freekicks_order|||
|corners_and_indirect_freekicks_text|||
|direct_freekicks_order|||
|direct_freekicks_text|||
|penalties_order|||
|penalties_text|||

### Position data (`element_types`)
The `element_types` field contains data for the position codes used in the `element_type` column of the player table.

```python
r = requests.get(fpl_url + 'bootstrap-static/')

players = pd.json_normalize(
    r.json()['element_types']
)
```

|column|dtype|description|
|---|---|---|
|id|||
|plural_name|||
|plural_name_short|||
|singular_name|||
|singular_name_short|||
|squad_select|||
|squad_min_play|||
|squad_max_play|||
|ui_shirt_specific|||
|sub_positions_locked|||
|element_count|||

### Team data (`teams`)
The `teams` field contains data for every active team in the current season.

```python
r = requests.get(fpl_url + 'bootstrap-static/')

players = pd.json_normalize(
    r.json()['teams']
)
```

|column|dtype|description|
|---|---|---|
|code|||
|draw|||
|form|||
|id|||
|loss|||
|name|||
|played|||
|points|||
|position|||
|short_name|||
|strength|||
|team_division|||
|unavailable|||
|win|||
|strength_overall_home|||
|strength_overall_away|||
|strength_attack_home|||
|strength_attack_away|||
|strength_defence_home|||
|strength_defence_away|||
|pulse_id|||

### Gameweek history
Individual player gameweek history can be retrieved from `https://fantasy.premierleague.com/api/element-summary/{player-id}/`

The function below takes a `player_id` as input and returns their full gameweek history for the current season:
```python
def get_gameweek_history(player_id):
    
    df = pd.json_normalize(
        requests.get(fpl_url + 'element-summary/' + str(player_id) + '/').json()['history']
    )
    
    return df

history = get_gameweek_history(1)
```
This function can be applied across all players to create a dataframe of all player gameweek scores:
```python
players = players['id'].apply(get_gameweek_history)
```
The resulting dataframe can then be merged with the player, position and team dataframes