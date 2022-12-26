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

# def _find_field_in_json(data, field, containing='track'):
#     if isinstance(data, dict):
#         # If the data is a dictionary, check the keys
#         for key, value in data.items():
#             if key == field and containing in value:
#                 # If the key is the field we are looking for, return the value
#                 return value
#             else:
#                 # If the key is not the field we are looking for, search the value recursively
#                 result = _find_field_in_json(value, field)
#                 if result is not None:
#                     return result
#     elif isinstance(data, list):
#         # If the data is a list, search each element recursively
#         for item in data:
#             result = _find_field_in_json(item, field)
#             if result is not None:
#                 return result
#     return None


# def get_S_data_with_tmp_token(url, token):
#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#         "Authorization": "Bearer {}".format(token)
#     }

#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("An error occurred: {}".format(response.status_code))


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

def get_S_data_with_app(track_name, artist_name):
  client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
  sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
  results = sp.search(q='track:' + track_name + ' artist:' + artist_name, type='track', limit=1)
  return results


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

    track_name = item_info['title']
    # print(track_name)

    track_artist = item_info['artist']['name']
    # print(track_artist)

    # track_name_formatted = track_name.replace(' ', '%2520').lower()
    # track_artist_formatted = track_artist.replace(' ', '%2520').lower()
    # URL = f"https://api.spotify.com/v1/search?q=remaster%2520track%3A{track_name}%2520artist%3A{track_artist}&type=track&limit=1"
    # TOKEN = "BQCDwTdv050QGun1Tg0ZVvLFRmNPGWjhGjulpXNExE3Jl6BBt673LBMrmolu66RLv4SHplJmnTo7A3muSdpocRl-1SPXbsstrpaikXinKXzAGqT9BSHeSQnK9_afcMKp3iYxshd_IvX8e1XpccQBldrmGCIcWaB7cWQQpVj-cYFKlKm4"
    # spotify_track_data = get_spotify_data_with_temporary_token(URL, TOKEN)
    # spotify_track_link = _find_field_in_json(spotify_track_data, "spotify", containing='track')
    # pp.pprint(spotify_track_link)

    spotify_track_data = get_S_data_with_app(track_name, track_artist)
    print(spotify_track_data['tracks']['items'][0]['external_urls']['spotify'])