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

spe_chars = ['&', '"', '#', '%', "'", '*', '+', ',', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '(', ')']
spe_chars_with_replace = ['  ']


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
    for char in spe_chars:
        if char in string:
            string = string.replace(char, '')

    for char in spe_chars_with_replace:
        if char in string:
            string = string.replace(char, ' ')
    
    return string.lower()


def get_S_results(track_name, artist_name, album_name):
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    query = 'track:' + track_name + ' artist:' + artist_name + ' album:' + album_name
    print(f'-> Query = {query}\n')
    results = sp.search(q=query, limit=1, type='track')
    
    if results['tracks']['total'] == 0:
        print('/!\ No results found with album, searching without album')
        query = 'track:' + track_name + ' artist:' + artist_name
        print(f'-> Query = {query}\n')
        results = sp.search(q=query, limit=1, type='track')
        
        if results['tracks']['total'] == 0:
            print('/!\ No results found with artist, searching without artist')
            query = 'track:' + track_name
            print(f'-> Query = {query}\n')
            results = sp.search(q=query, limit=1, type='track')
            
            if results['tracks']['total'] == 0:
                raise Exception('No results found')

    print('-> Results found:')
    return query, results


def choose_result(results):
    for i, item in enumerate(results['tracks']['items']):
        print("%d: %s - %s" % (i, item['artists'][0]['name'], item['name']))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('deezer_link', type = str)
    args = parser.parse_args()

    # Get the final link after redirection
    item_final_link = get_D_final_url(args.deezer_link)

    # Parse the support and id from the final link
    item_type, item_id = get_D_item_identifiers(item_final_link)
    item_info = get_D_info(item_type, int(item_id))
    # print(item_info)

    track_name = preprocess_string(item_info['title'])
    artist_name = preprocess_string(item_info['artist']['name'])
    album_name = preprocess_string(item_info['album']['title'])
    # print(f'Searching for: {track_name} by {artist_name} in {album_name}')

    S_query, S_results = get_S_results(track_name, artist_name, album_name)
    # print(spotify_results)
    print(S_results['tracks']['items'][0]['external_urls']['spotify'])