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

|:key: id|first_name|second_name|web_name|element_type|team|total_points|dreamteam_count|in_dreamteam|now_cost|points_per_game|minutes|goals_scored|assists|clean_sheets|goals_conceded|own_goals|penalties_saved|penalties_missed|yellow_cards|red_cards|saves|bonus|bps|influence|creativity|threat|ict_index|influence_rank|influence_rank_type|creativity_rank|creativity_rank_type|threat_rank|threat_rank_type|ict_index_rank|ict_index_rank_type|
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|1|Mesut|Özil|Özil|3|1|0|0|False|68|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|604|240|604|240|604|240|604|240|
|2|Sokratis|Papastathopoulos|Sokratis|2|1|0|0|False|49|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|566|212|556|212|543|206|567|212|
|3|David|LuizMoreiraMarinho|DavidLuiz|2|1|7|0|False|55|1.2|364|0|0|0|7|0|0|0|0|0|0|0|52|72|23.1|22|11.7|239|93|270|79|267|78|297|100|
|4|Pierre-Emerick|Aubameyang|Aubameyang|3|1|37|0|False|115|3.4|986|2|1|3|14|0|0|0|2|0|0|1|123|141.4|170.8|277|58.9|135|51|42|30|31|15|36|20|
|5|Cédric|Soares|Cédric|2|1|0|0|False|46|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|542|206|529|206|504|197|543|206|

### Position data (`element_types`)
The `element_types` field contains data for the position codes used in the `element_type` column of the player table.

```python
r = requests.get(fpl_url + 'bootstrap-static/')

players = pd.json_normalize(
    r.json()['element_types']
)
```

|:key: id|plural_name|plural_name_short|singular_name|
| --- | --- | --- | --- |
|1|Goalkeepers|GKP|Goalkeeper|
|2|Defenders|DEF|Defender|
|3|Midfielders|MID|Midfielder|
|4|Forwards|FWD|Forward|

### Team data (`teams`)
The `teams` field contains data for every active team in the current season.

```python
r = requests.get(fpl_url + 'bootstrap-static/')

players = pd.json_normalize(
    r.json()['teams']
)
```

|:key: id|name|short_name|strength|strength_overall_home|strength_overall_away|strength_attack_home|strength_attack_away|strength_defence_home|strength_defence_away|
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|1|Arsenal|ARS|4|1190|1210|1170|1210|1190|1200|
|2|AstonVilla|AVL|3|1150|1160|1150|1150|1180|1210|
|3|Brighton|BHA|3|1080|1100|1150|1180|1090|1100|
|4|Burnley|BUR|2|1050|1080|1120|1190|1010|1030|
|5|Chelsea|CHE|4|1260|1280|1240|1280|1270|1310|
|6|CrystalPalace|CRY|3|1110|1150|1100|1150|1020|1050|
|7|Everton|EVE|3|1180|1210|1150|1170|1210|1250|
|8|Fulham|FUL|2|1000|1020|1020|1030|1020|1020|
|9|Leicester|LEI|4|1220|1240|1190|1190|1200|1180|
|10|Leeds|LEE|3|1100|1130|1060|1110|1130|1160|
|11|Liverpool|LIV|5|1320|1360|1240|1320|1330|1350|
|12|ManCity|MCI|5|1310|1360|1260|1320|1330|1350|
|13|ManUtd|MUN|4|1230|1230|1220|1230|1250|1260|
|14|Newcastle|NEW|3|1100|1130|1100|1120|1010|1060|
|15|SheffieldUtd|SHU|3|1070|1100|1110|1130|1010|1050|
|16|Southampton|SOU|3|1150|1180|1140|1200|1110|1160|
|17|Spurs|TOT|4|1270|1280|1190|1240|1280|1320|
|18|WestBrom|WBA|2|1010|1030|1020|1020|1000|1010|
|19|WestHam|WHU|3|1140|1170|1150|1160|1170|1180|
|20|Wolves|WOL|3|1160|1190|1180|1220|1100|1170|

### Gameweek history
Individual player gameweek history can be retrieved from `https://fantasy.premierleague.com/api/element-summary/{player-id}/`

The function below takes a `player_id` as input and returns their full gameweek history for the current season:
```python
def get_gameweek_history(player_id):
    
    df = pd.json_normalize(
        requests.get(fpl_url + 'element-summary/' + str(player_id) + '/').json()['history']
    )
    
    return df

get_gameweek_history(24)

```
`Out:`

|element|fixture|opponent_team|total_points|was_home|kickoff_time|team_h_score|team_a_score|round|minutes|goals_scored|assists|clean_sheets|goals_conceded|own_goals|penalties_saved|penalties_missed|yellow_cards|red_cards|saves|bonus|bps|influence|creativity|threat|ict_index|value|transfers_balance|selected|transfers_in|transfers_out|
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|24|2|8|0|False|2020-09-12T11:30:00Z|0|3|1|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|55|0|491508|0|0|
|24|9|19|2|True|2020-09-19T19:00:00Z|2|1|2|88|0|0|0|1|0|0|0|0|0|0|0|8|7.4|20.3|30|5.8|54|-145334|357292|7716|153050|
|24|23|11|0|False|2020-09-28T19:00:00Z|3|1|3|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|54|-81091|286264|14805|95896|
|24|29|15|8|True|2020-10-04T13:00:00Z|2|1|4|86|1|0|0|1|0|0|0|0|0|0|1|29|40.6|6|53|10|53|-47534|243259|9105|56639|
|24|44|12|2|False|2020-10-17T16:30:00Z|1|0|5|90|0|0|0|1|0|0|0|0|0|0|0|18|20.6|17.5|38|7.6|53|-24953|224096|16280|41233|

This function can be applied across all players to create a dataframe of all player gameweek scores:
```python
players = players['id'].apply(get_gameweek_history)
```
The resulting dataframe can then be merged with the player, position and team dataframes