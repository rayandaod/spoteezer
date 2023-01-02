import json
import argparse
import pprint
import spotipy
import os
import logging

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


def check_deezer_link(deezer_link, logger=None):
    """
    Check if the Deezer link is valid.
    """

    if deezer_link is None:
        return None

    # Remove whitespace and replace http with https
    deezer_link = deezer_link.strip()
    deezer_link = deezer_link.replace('http://', 'https://')
    
    # Get the final link after redirections
    deezer_link = get_final_url(deezer_link, logger=logger)

    if deezer_link.startswith('https://www.deezer.com/'):
        return deezer_link

    return None


def get_deezer_data_from_url(url, logger=None):
    """
    Get the data from the Deezer API.
    """

    connection.request("GET", url)
    response = connection.getresponse()
    return json.loads(response.read().decode("utf-8"))


def get_deezer_item_type_id(url, logger=None):
    """
    Get the item type and id from the Deezer link.
    The item type is a string that can be either 'track', 'album' or 'artist'.
    The item id is the id of the item in Deezer's database.
    """

    item_type = url.split('/')[-2]
    item_id = int(url.split('/')[-1].split('?')[0])

    if logger is not None:
        logger.info(f'Deezer item type = {item_type}')
        logger.info(f'Deezer item id = {item_id}')

    return item_type, item_id


def get_raw_deezer_item_info(support, id, logger=None):
    """
    Get the item info from the Deezer API.
    The support is a string that can be either 'track', 'album' or 'artist'.
    The id is the id of the item in Deezer's database.
    """

    url = deezer_api + "%s/%d" % (support, id)
    return get_deezer_data_from_url(url)


def get_deezer_item_info(deezer_item_type, deezer_item_info, logger=None):
    if deezer_item_type == 'track':
        deezer_item_info = {
            'track': preprocess_string(deezer_item_info['title']),
            'artist': preprocess_string(deezer_item_info['artist']['name']),
            'album': preprocess_string(deezer_item_info['album']['title'])
        }

    elif deezer_item_type == 'album':
        deezer_item_info = {
            'album': preprocess_string(deezer_item_info['title']),
            'artist': preprocess_string(deezer_item_info['artist']['name'])
        }

    elif deezer_item_type == 'artist':
        deezer_item_info = {
            'artist': preprocess_string(deezer_item_info['name'])
        }

    if logger is not None:
        logger.info(f'Deezer item info = {deezer_item_info}')
    
    return deezer_item_info


def search_spotify_item(search_dict, item_type, logger=None):
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
        
        if logger is not None:
            logger.info(f'Spotify query = {query}')

        return query

    found = False
    trial_index = 0
    while not found:
        if logger is not None:
            logger.info(f'Trying {trials[trial_index]}...')

        trial = trials[trial_index]
        spotify_query = _get_query(trial)
        spotify_results = SPOTIFY.search(q=spotify_query, limit=1, type=item_type)
        found = spotify_results[item_type+'s']['total'] > 0
        
        if not found and trial_index == len(trials) - 1:
            error_msg = f'Could not find {item_type} in Spotify.'
            if logger is not None:
                logger.info(error_msg)
            raise FileNotFoundError(error_msg)
        else:
            trial_index += 1
    
    return spotify_results


def get_spotify_link_from_results(spotify_results, item_type, logger=None):
    spotify_link = get_first_value_with_substr(spotify_results, 'spotify', substring=item_type)

    if logger is not None:
        logger.info(f'Spotify link = {spotify_link}')

    return spotify_link


def convert_deezer_to_spotify(deezer_link, logger=None):

    # ----- DEEZER -----

    # Parse the item type and id from the final deezer link
    deezer_item_type, deezer_item_id = get_deezer_item_type_id(deezer_link, logger=logger)

    # Get the item info from the Deezer API
    deezer_raw_item_info = get_raw_deezer_item_info(deezer_item_type, deezer_item_id, logger=logger)

    # Get the search dict to search for the item in Spotify
    deezer_item_info = get_deezer_item_info(deezer_item_type, deezer_raw_item_info, logger=logger)

    # ----- SPOTIFY -----
    
    # Search for the item in Spotify
    spotify_results = search_spotify_item(deezer_item_info, deezer_item_type, logger=logger)

    # Get the Spotify link from the results
    spotify_link = get_spotify_link_from_results(spotify_results, deezer_item_type, logger=logger)

    return spotify_link


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('deezer_link', type=str)
    args = parser.parse_args()

    deezer_link = args.deezer_link
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    spotify_link = convert_deezer_to_spotify(deezer_link, logger=logger)
    print(spotify_link)
