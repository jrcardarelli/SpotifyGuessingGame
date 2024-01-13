from flask import Flask, redirect, render_template, request, jsonify
import spotipy
import Authorization
from localStoragePy import localStoragePy
import urllib.parse as urlparse
import requests
from urllib.parse import urlencode
from spotipy.oauth2 import SpotifyClientCredentials

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
clientId = os.environ.get('SPOTIPY_CLIENT_ID')
redirectUri = 'http://localhost:5000'

app = Flask(__name__)


@app.route('/callback')
def callback():
    code = request.args.get('code')

    localStorage = localStoragePy('spotify.game', 'json')
    codeVerifier = localStorage.getItem('code_verifier')
    token_endpoint = "https://accounts.spotify.com/api/token"

    payload = {
        "client_id": clientId,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirectUri,
        "code_verifier": codeVerifier,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(token_endpoint, data=payload, headers=headers)

    access_token = None

    if response.status_code == 200:
        # Assuming the response is in JSON format
        response_data = response.json()
        access_token = response_data.get('access_token')

        # Store the access token in local storage or perform further actions
        localStorage.setItem('access_token', access_token)
    else:
        print("Error:", response.text)

    return access_token

@app.route('/')
def hello_world():  # put application's code here'

    return render_template('index.html')


@app.route('/test')
def test():
    codeVerifier = Authorization.generate_random_string(64)
    hashed = Authorization.hash_verifier(codeVerifier)
    codeChallenge = Authorization.base64encode(hashed)

    scope = 'user-read-private user-read-email user-top-read'
    authUrl = 'https://accounts.spotify.com/authorize'

    localStorage = localStoragePy('spotify.game', 'json')
    localStorage.setItem('code_verifier', codeVerifier)

    params = {
        "response_type": "code",
        "client_id": clientId,
        "scope": scope,
        "code_challenge_method": "S256",
        "code_challenge": codeChallenge,
        "redirect_uri": redirectUri
    }

    url_parts = list(urlparse.urlparse(authUrl))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)
    # redirect(location=urlparse.urlunparse(url_parts))

    return redirect(location=urlparse.urlunparse(url_parts))

    # return(urlparse.urlunparse(url_parts))

    # dummy_user = spotipy.Spotify.user()


@app.route('/get_new_image')
def get_new_image():
    # You can replace this with logic to fetch a dynamic image URL

    lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.artist_top_tracks(lz_uri)
    result = ""
    for track in results['tracks'][:10]:
        print('track    : ' + track['name'])
        print('audio    : ' + track['preview_url'])
        print('cover art: ' + track['album']['images'][0]['url'])
        result = track['album']['images'][0]['url']

    return jsonify({'new_image_url': result})


if __name__ == '__main__':
    app.run()
