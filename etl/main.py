import pymongo
import requests


BASE_URL = 'https://fantasy.premierleague.com/api/'

# db.positions.insert_many(api_data['element_types'])
# db.teams.insert_many(api_data['teams'])


# get data from api
api_data = requests.get(BASE_URL+'bootstrap-static/').json()

# extract player data
players = api_data['elements']

# rename id column to fit mongodb primary key requirements
for p in players:
    p['_id'] = p.pop('id')

# upload to mongodb client (replace <password> with actual password)
client = pymongo.MongoClient('mongodb+srv://steinar:<password>@fpl-cluster.ygbi5gm.mongodb.net/?retryWrites=true&w=majority')
db = client.raw

# ToDo: this doesn't work
db.players.update_many(players, upsert=True)
