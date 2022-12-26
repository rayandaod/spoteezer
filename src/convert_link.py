import json
import argparse
import requests
import pprint
import spotipy

from http.client import HTTPSConnection

pp = pprint.PrettyPrinter(indent=4)

deezer_api = "/2.0/"
connection = HTTPSConnection("api.deezer.com")

SpotifyClientCredentials = spotipy.oauth2.SpotifyClientCredentials

with open('./../spotify_credentials.txt', 'r') as f:
    SPOTIFY_CLIENT_ID = f.readline().strip()
    SPOTIFY_CLIENT_SECRET = f.readline().strip()

SPOTIFY_CLIENT_CREDS = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
SPOTIFY = spotipy.Spotify(client_credentials_manager=SPOTIFY_CLIENT_CREDS)

SPE_CHARS = ['&', '"', '#', '%', "'", '*', '+', ',', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '(', ')']
SPE_CHARS_WITH_REPLACE = ['  ']


def get_first_value(data, key, string):
    if isinstance(data, dict):
        # Check if the current level contains the key
        if key in data and string in data[key]:
            return data[key]
        # Otherwise, recursively search the nested dictionaries
        for value in data.values():
            result = get_first_value(value, key, string)
            if result is not None:
                return result
    elif isinstance(data, list):
        # Recursively search the list elements
        for item in data:
            result = get_first_value(item, key, string)
            if result is not None:
                return result
    return None


def get_D_data(url):
    connection.request("GET", url)
    response = connection.getresponse()
    return json.loads(response.read().decode("utf-8"))


def get_D_info(support, id):
    url = deezer_api + "%s/%d" % (support, id)
    return get_D_data(url)


def get_D_final_url(url):
    responses = requests.get(url)

    if len(responses.history) > 0:
        return responses.history[-1].url
    else:
        return responses.url


def get_D_item_identifiers(url):
    item_type = url.split('/')[-2]
    item_id = url.split('/')[-1].split('?')[0]
    return item_type, item_id


def preprocess_string(string):
    for char in SPE_CHARS:
        if char in string:
            string = string.replace(char, '')

    for char in SPE_CHARS_WITH_REPLACE:
        if char in string:
            string = string.replace(char, ' ')
    
    return string.lower()


def get_S_tracks(track_name=None, artist_name=None, album_name=None):
    query = ''
    query += ('track:' + track_name) if track_name is not None else ''
    query += (' artist:' + artist_name) if artist_name is not None else ''
    query += (' album:' + album_name) if album_name is not None else ''
    print(f'-> Query = {query}\n')
    results = SPOTIFY.search(q=query, limit=1, type='track')
    
    if results['tracks']['total'] == 0:
        print('/!\ No results found with album, searching without album')
        query = ''
        query += ('track:' + track_name) if track_name is not None else ''
        query += (' artist:' + artist_name) if artist_name is not None else ''
        print(f'-> Query = {query}\n')
        results = SPOTIFY.search(q=query, limit=1, type='track')
        
        if results['tracks']['total'] == 0:
            print('/!\ No results found with artist, searching without artist')
            query = ''
            query += ('track:' + track_name) if track_name is not None else ''
            print(f'-> Query = {query}\n')
            results = SPOTIFY.search(q=query, limit=1, type='track')
            
            if results['tracks']['total'] == 0:
                raise Exception('No results found')

    print('-> Results found:')
    return query, results


def get_S_albums(album_name=None, artist_name=None):
    query = ''
    query += ('album:' + album_name) if album_name is not None else ''
    query += (' artist:' + artist_name) if artist_name is not None else ''
    print(f'-> Query = {query}\n')
    results = SPOTIFY.search(q=query, limit=1, type='album')
    
    if results['albums']['total'] == 0:
        print('/!\ No results found with artist, searching without artist')
        query = ''
        query += ('album:' + album_name) if album_name is not None else ''
        print(f'-> Query = {query}\n')
        results = SPOTIFY.search(q=query, limit=1, type='album')
    
    print('-> Results found:')
    return query, results


def get_S_artists(artist_name=None):
    query = ''
    query += ('artist:' + artist_name) if artist_name is not None else ''
    print(f'-> Query = {query}\n')
    results = SPOTIFY.search(q=query, limit=1, type='artist')

    print('-> Results found:')
    return query, results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('deezer_link', type = str)
    args = parser.parse_args()

    # Get the final link after redirection
    item_final_link = get_D_final_url(args.deezer_link)

    # Parse the support and id from the final link
    item_type, item_id = get_D_item_identifiers(item_final_link)
    item_info = get_D_info(item_type, int(item_id))

    if item_type == 'track':
        track_name = preprocess_string(item_info['title'])
        artist_name = preprocess_string(item_info['artist']['name'])
        album_name = preprocess_string(item_info['album']['title'])
        # print(f'Searching for: {track_name} by {artist_name} in {album_name}')
        S_query, S_results = get_S_tracks(track_name, artist_name, album_name)
    
    elif item_type == 'album':
        album_name = preprocess_string(item_info['title'])
        artist_name = preprocess_string(item_info['artist']['name'])
        # print(f'Searching for: {album_name} by {artist_name}')
        S_query, S_results = get_S_albums(album_name, artist_name)

    elif item_type == 'artist':
        artist_name = preprocess_string(item_info['name'])
        # print(f'Searching for: {artist_name}')
        S_query, S_results = get_S_artists(artist_name)

    # print(get_all_values_for_key(S_results, 'spotify'))

    link = get_first_value(S_results, 'spotify', item_type)
    print(link)
