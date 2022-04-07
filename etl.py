from secrets import CLIENT_ID, CLIENT_SECRET
from client import spotifyClient
from db.db import tracks, engine 
import numpy as np

# get models
import pickle

with open('models/sc.pickle', 'rb') as f:
    sc = pickle.load(f)

with open('models/cluster_model.pickle', 'rb') as f:
    model = pickle.load(f)


# get data from api
spotify = spotifyClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify.perform_auth()
if not spotify.perform_auth():
  print("Could not authenticate to spotify api, check credentials")

# connect to db
conn = engine.connect()


# ETL pipeline
def insert_to_db(track_name, artist_name):
  
  trackMeta = spotify.search(query = {'track':track_name, 'artist':artist_name}, search_type="track")
  uri = trackMeta["tracks"]["items"][0]["id"]
  
  features = spotify.get_audio_features(uri)

  energy = features['energy']
  valence = features['valence']
  acousticness = features['acousticness']
  liveness = features['liveness']


  X = [energy,valence, acousticness,liveness]
  X = sc.transform([X])
  cluster = model.predict(X)[0]
  X = X[0]

  insert = tracks.insert().values(
  artist_name = artist_name,
  track_name = track_name,
  cluster = cluster,
  energy = X[0],
  valence = X[1],
  acousticness = X[2],
  liveness = X[3],
  )

  conn.execute(insert)


insert_to_db(track_name="in da club", artist_name="50 cent")

conn.close()
