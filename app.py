from flask import Flask, redirect, render_template, request, jsonify
import spotipy
import Authorization
import json_parsing
from localStoragePy import localStoragePy
import urllib.parse as urlparse
import requests
from urllib.parse import urlencode
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Load environment variables from .env file
load_dotenv()
clientId = os.environ.get('SPOTIPY_CLIENT_ID')
redirectUri = 'http://localhost:5000'
access_token = ''

app = Flask(__name__)

# Replace these variables with your AWS RDS connection details
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')

# Configure SQLAlchemy to use PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# db = SQLAlchemy(app)


# Models
class Score(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    high_score = db.Column(db.Integer, unique=False, nullable=False)
    display_name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Id: {self.id}, Score: {self.high_score}"


# Create tables only if they do not exist
with app.app_context():
    db.create_all()


@app.route('/')
def hello_world():  # put application's code here
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

    if response.status_code == 200:
        # Assuming the response is in JSON format
        response_data = response.json()
        global access_token
        access_token = response_data.get('access_token')

        # Store the access token in local storage or perform further actions
        localStorage.setItem('access_token', access_token)
    else:
        print("Error:", response.text)

    return render_template('index.html')


@app.route('/test')
def test():
    codeVerifier = Authorization.generate_random_string(64)
    hashed = Authorization.hash_verifier(codeVerifier)
    codeChallenge = Authorization.base64encode(hashed)

    scope = 'user-read-recently-played user-read-private user-read-email'
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

    return redirect(location=urlparse.urlunparse(url_parts))


@app.route('/test_user_data')
def test_user_data():
    if access_token != '':
        url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
        headers = {
            "Authorization": "Bearer " + access_token,
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            try:
                json_response = response.json()

                collected_tracks = json_parsing.collect_recent_tracks(json_response)

                return {
                    "random_songs": collected_tracks["names"],
                    "previews": collected_tracks["previews"],
                    "artists": collected_tracks["artists"],
                    "covers": collected_tracks["covers"],
                    "dates": collected_tracks["dates"],
                }
            except ValueError as e:
                print("Error decoding JSON:", e)
                return jsonify({'error': 'Invalid JSON in response'})
        else:
            print("Error:", response.text)
            return jsonify({'error': 'Request failed'})

    else:
        print("UH OH THAT'S BAD")
        return 0


@app.route('/retrieve_user_name')
def retrieve_user_name():
    if access_token != '':
        url = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": "Bearer " + access_token,
        }

        response = requests.get(url, headers=headers)
        json_data_stuff = response.json()
        display_name = json_parsing.get_user_display_name(json_data_stuff)

        return {
            "display_name": display_name
        }
    else:
        return {
            "display_name": "Sign in to Spotify to begin"
        }


@app.route('/check_signed_in')
def check_signed_in():
    if access_token != '':
        return {"signedIn": True}
    else:
        return {"signedIn": False}


@app.route('/new_score/<int:score>')
def new_score(score):
    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": "Bearer " + access_token,
    }

    response = requests.get(url, headers=headers)
    json_data_stuff = response.json()
    display_name = json_parsing.get_user_display_name(json_data_stuff)
    row = Score.query.filter_by(id=json_parsing.get_user_id(json_data_stuff)).first()
    if not row:
        score_obj2 = Score(
            id=json_parsing.get_user_id(json_data_stuff),
            high_score=score,
            display_name=display_name
        )
        db.session.add(score_obj2)
        db.session.commit()
    else:

        if row.high_score > score:
            print("updating")
            print(score)
            row.high_score = score
            db.session.commit()

    return "200"


@app.route('/get_high_score')
def get_high_score():
    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": "Bearer " + access_token,
    }

    response = requests.get(url, headers=headers)
    json_data_stuff = response.json()
    row = Score.query.filter_by(id=json_parsing.get_user_id(json_data_stuff)).first()

    if not row:
        print("returning nothing")
        return {"high_score": -1}
    else:
        return {"high_score": row.high_score}


@app.route('/get_high_scores')
def get_high_scores():
    # Fetch the results from the ResultProxy
    result_proxy = db.session.execute(db.select(Score.display_name, Score.high_score).order_by(Score.high_score))

    # Convert the results into a list of dictionaries
    scores = [{'display_name': row[0], 'high_score': row[1]} for row in result_proxy.fetchall()]

    print(scores)

    # Use jsonify to convert the list of dictionaries to JSON
    return jsonify(scores)


if __name__ == '__main__':
    app.run()
