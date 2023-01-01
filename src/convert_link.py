import json
import argparse
import requests
import pprint
import spotipy
import os

from http.client import HTTPSConnection

from helper import *

pp = pprint.PrettyPrinter(indent=4)

# Deezer API
deezer_api = "/2.0/"
connection = HTTPSConnection("api.deezer.com")

# Spotify API credentials
SpotifyClientCredentials = spotipy.oauth2.SpotifyClientCredentials
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_CLIENT_CREDS = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
SPOTIFY = spotipy.Spotify(client_credentials_manager=SPOTIFY_CLIENT_CREDS)


def get_deezer_data_from_url(url):
    """
    Get the data from the Deezer API.
    """

    connection.request("GET", url)
    response = connection.getresponse()
    return json.loads(response.read().decode("utf-8"))


def get_deezer_item_type_id(url):
    """
    Get the item type and id from the Deezer link.
    The item type is a string that can be either 'track', 'album' or 'artist'.
    The item id is the id of the item in Deezer's database.
    """

    item_type = url.split('/')[-2]
    item_id = int(url.split('/')[-1].split('?')[0])
    return item_type, item_id


def get_deezer_item_info(support, id):
    """
    Get the item info from the Deezer API.
    The support is a string that can be either 'track', 'album' or 'artist'.
    The id is the id of the item in Deezer's database.
    """

    url = deezer_api + "%s/%d" % (support, id)
    return get_deezer_data_from_url(url)


def search_spotify_item(search_dict, item_type):
    """
    Search for a Spotify item using the search_dict and item_type.
    The search_dict is a dictionary with the following keys
    - track
    - artist
    - album
    The item_type is a string that can be either 'track', 'album' or 'artist'.
    """

    # Get the trials corresponding to the item_type
    trials = SEARCH_TRIAL_DICT[item_type]

    def _get_query(trial):
        """
        Get the query string from the search_dict and trial.
        The trial is a list of keys from the search_dict.
        """

        query = ''
        for key in trial:  # e.g ['track', 'artist', 'album']
            value = search_dict[key]
            query += (f'{key}:' + value + ' ') if value is not None else ''
        print(f'-> Query = {query}\n')
        return query

    found = False
    trial_index = 0
    while not found:
        print(f'Trying {trials[trial_index]}...')
        trial = trials[trial_index]
        spotify_query = _get_query(trial)
        spotify_results = SPOTIFY.search(q=spotify_query, limit=1, type=item_type)
        found = spotify_results[item_type+'s']['total'] > 0
        if trial_index == len(trials) - 1:
            break
        else:
            trial_index += 1
    
    return spotify_query, spotify_results


def get_spotify_link_from_results(spotify_results, item_type):
    return get_first_value_with_substr(spotify_results, 'spotify', substring=item_type)


def convert_deezer_to_spotify(deezer_link):
    # Get the final link after redirections
    final_url = get_final_url(deezer_link)

    # Parse the item type and id from the final deezer link
    item_type, item_id = get_deezer_item_type_id(final_url)

    # Get the item info from the Deezer API
    item_info = get_deezer_item_info(item_type, item_id)

    if item_type == 'track':
        track_name = preprocess_string(item_info['title'])
        artist_name = preprocess_string(item_info['artist']['name'])
        album_name = preprocess_string(item_info['album']['title'])
        # print(f'Searching for: {track_name} by {artist_name} in {album_name}')
        search_dict = {
            'track': track_name,
            'artist': artist_name,
            'album': album_name
        }
        spotify_query, spotify_results = search_spotify_item(search_dict, item_type)
        # print(f'Spotify query = {spotify_query}')

    elif item_type == 'album':
        album_name = preprocess_string(item_info['title'])
        artist_name = preprocess_string(item_info['artist']['name'])
        # print(f'Searching for: {album_name} by {artist_name}')
        search_dict = {
            'album': album_name,
            'artist': artist_name
        }
        spotify_query, spotify_results = search_spotify_item(search_dict, item_type)
        # print(f'Spotify query = {spotify_query}')

    elif item_type == 'artist':
        artist_name = preprocess_string(item_info['name'])
        # print(f'Searching for: {artist_name}')
        search_dict = {
            'artist': artist_name
        }
        spotify_query, spotify_results = search_spotify_item(search_dict, item_type)
        # print(f'Spotify query = {spotify_query}')

    spotify_link = get_spotify_link_from_results(spotify_results, item_type)

    return spotify_link


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('deezer_link', type=str)
    args = parser.parse_args()

    deezer_link = args.deezer_link
    spotify_link = convert_deezer_to_spotify(deezer_link)
    print(spotify_link)
