from typing import Mapping
from unicodedata import name
import pymongo
import requests
import config

BASE_URL = 'https://fantasy.premierleague.com/api/'

# get data from api
api_data = requests.get(BASE_URL+'bootstrap-static/').json()

# extract player data
players = api_data['elements']

# rename id column to fit mongodb primary key requirements
for p in players:
    p['_id'] = p.pop('id')



# upload to mongodb client (replace <password> with actual password)
client = pymongo.MongoClient('mongodb+srv://' + config.username + ':' + config.password + '@fpl-cluster.ygbi5gm.mongodb.net/?retryWrites=true&w=majority')

db = client.get_database('raw')

#Update each player in mongodb players database
for p in players:
    player_id = p['_id']
    db.players.replace_one(
        filter = {'_id': player_id},
        replacement = p,
        upsert = True
    )