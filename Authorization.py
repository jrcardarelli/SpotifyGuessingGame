import spotipy
import random
import hashlib
import base64
from spotipy.oauth2 import SpotifyClientCredentials


def generate_random_string(length):
    result = ""
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    rand = random.randint(0, 61)

    for i in range(length):
        result += possible[rand]

    return result


def hash_verifier(verifier):
    encoded_data = verifier.encode('utf-8')
    return hashlib.sha256(encoded_data).digest()


def base64encode(hashed):
    encoded_data = base64.b64encode(hashed).decode('utf-8')
    encoded_data = encoded_data.replace('=', '').replace('+', '-').replace('/', '_')
    return encoded_data
