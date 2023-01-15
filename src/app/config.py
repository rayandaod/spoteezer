import os
import spotipy
import deezer


# Deezer API
DEEZER = deezer.Client()

# Spotify API credentials
SpotifyClientCredentials = spotipy.oauth2.SpotifyClientCredentials
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_CLIENT_CREDS = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
SPOTIFY = spotipy.Spotify(client_credentials_manager=SPOTIFY_CLIENT_CREDS)