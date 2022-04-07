from secrets import CLIENT_ID, CLIENT_SECRET
import requests
import base64
import datetime
from urllib.parse import urlencode

client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
client_creds_b64 = base64.b64encode(client_creds.encode())


client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
client_creds_b64 = base64.b64encode(client_creds.encode())


class spotifyClient(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_creds(self):

        client_id = self.client_id
        client_secret = self.client_secret

        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64

    def get_token_headers(self):
        client_creds_b64 = self.get_client_creds()
        return {
            "Authorization": f"Basic {client_creds_b64.decode()}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):

        url = self.url
        token_data = self.get_token_data()
        headers = self.get_token_headers()
        r = requests.post(url, data=token_data, headers=headers)

        if r.status_code != 200:
            return Exception("Auth error occured")

        data = r.json()
        now = datetime.datetime.now()
        access_token = data["access_token"]
        self.access_token = access_token
        expires_in = data["expires_in"]
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):

        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_recourse_header(self):
        access_token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        return headers

    def get_recourse(self, _id, resource_type, item_type, market_id):
        endpoint = f"https://api.spotify.com/v1/{resource_type}/{_id}/{item_type}?market={market_id}"
        headers = self.get_recourse_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code != 200:
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_recourse(_id, resource_type="albums")

    def get_artist(self, _id):
        return self.get_recourse(_id, resource_type="artists")

    def get_playlist(self, _id):
        return self.get_recourse(_id, resource_type="playlists", item_type="tracks", market_id="SE")

    def get_audio_features(self, _id):
        return self.get_recourse(_id, resource_type="audio-features", item_type="", market_id="")

    def get_tracks(self):
        pass

    def base_search(self, query_params):

        headers = self.get_recourse_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code == 200:
            return r.json()
        return {}

    def search(self, query=None, search_type=None, market_id="SE"):
        if isinstance(query, type({})):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        query_params = urlencode({
            'q': query.lower(), 'type': search_type.lower(), 'market': market_id
        })
        return self.base_search(query_params)

    def get_id_from_track(self, track_name):

        track = self.search(
            query=track_name, search_type="track", market_id="SE")
        uri = track["tracks"]["items"][0]["id"]
        features = self.get_audio_features(_id=uri)
        return features
