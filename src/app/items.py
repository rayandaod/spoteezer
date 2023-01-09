import json
import pprint
import requests

from urllib.parse import urlparse, quote

from helper import get_first_value_with_substr, preprocess_string
from config import DEEZER_CONNECTION, DEEZER_API, SPOTIFY


pp = pprint.PrettyPrinter(indent=4)

# Search parameters dictionary
# The key is the type of the item (track, album, artist)
# The value is a list of lists of search terms, in order of priority
SEARCH_PARAM_TRIALS_DICT = {'track': [['track', 'artist', 'album'],
                                    ['track', 'artist'],
                                    ['track']],
                          'album': [['album', 'artist'],
                                    ['album']],
                          'artist': [['artist']]
                          }


class Item():
    def __init__(self, link):
        # Check if the link is valid
        if link is None:
            raise ValueError('Link is None')

        # Remove whitespace and replace http with https
        tmp_link = link.strip()
        tmp_link = link.replace('http://', 'https://')

        # Get the final link after redirections
        responses = requests.get(tmp_link)
        if len(responses.history) > 0:
            self.link = responses.history[-1].url
        else:
            self.link = responses.url

    
    def extract_info_simple(self, artists_key=None, item_name_key=None):
        """
        Get the specified information from the Spotify results.
        """

        # Initialize the info dictionary
        info_simple = {}

        # Get the artist or artists
        def _get_artists(info_simple, raw_info, artists_key):
            if type(self) == DeezerItem and artists_key not in raw_info:
                artists_key = 'artist'

            if type(raw_info[artists_key]) == list and len(raw_info[artists_key]) > 1:
                info_simple['artists'] = ', '.join(
                    [raw_info[artists_key][i]['name'] for i in range(len(raw_info[artists_key]))])
            else:
                info_simple['artist'] = raw_info[artists_key][0]['name'] if type(
                    raw_info[artists_key]) == list else raw_info[artists_key]['name']
            return info_simple

        # For each info type, get the corresponding info from the item
        if self.type in ['track', 'album']:
            info_simple[self.type] = self.raw_info[item_name_key]
            info_simple = _get_artists(info_simple, self.raw_info, artists_key)

            if self.type == 'track':
                info_simple['album'] = self.raw_info['album'][item_name_key]

        elif self.type == 'artist':
            if type(self) == DeezerItem:
                info_simple['artist'] = self.raw_info['artist']['name']
            else:
                info_simple['artist'] = self.raw_info['name']

        return info_simple


    def extract_img_link(self, key, substr=None):
        img_link = get_first_value_with_substr(self.raw_info, key, substr)
        return img_link


    def extract_web_info(self, logger=None):
        web_info = {'resultLink': self.link,
                    'img_src': self.img_link,
                    'info': self.info_simple,
                    'type': self.type}

        return web_info


class DeezerItem(Item):
    def __init__(self, link=None, search_params=None, item_type=None, logger=None):
        self.logger = logger

        if link is not None:
            super().__init__(link)
            self.type = self.link.split('/')[-2]
            self.id = int(self.link.split('/')[-1].split('?')[0])
            self.raw_info = self.get_raw_info_from_id(self.id, self.type)
            self.search_params = self.get_search_params(self.raw_info)

        elif search_params is not None:
            self.search_params = search_params
            self.type = item_type
            results = self.search(self.search_params, self.type)
            self.raw_info = self.get_raw_info_from_results(results)
            self.id = self.raw_info['id']
            self.link = self.raw_info['link']
        
        self.img_link = self.extract_img_link('cover_medium', 'cover')
        self.info_simple = self.extract_info_simple(artists_key='contributors', item_name_key='title')
        self.web_info = self.extract_web_info()

    
    def get_raw_info_from_id(self, id, _type):
        link_clean = DEEZER_API + f"{_type}/{id}"

        # Get the data from the Deezer API
        DEEZER_CONNECTION.request("GET", link_clean)
        response = DEEZER_CONNECTION.getresponse()

        # Check if the response is valid
        if response.status != 200:
            raise ValueError('Invalid response from Deezer API')

        return json.loads(response.read().decode("utf-8"))


    def get_raw_info_from_results(self, results):
        return results['data'][0]

    
    def get_search_params(self, raw_info):
        if self.type == 'track':
            search_params = {
                'track': preprocess_string(raw_info['title']),
                'artist': preprocess_string(raw_info['artist']['name']),
                'album': preprocess_string(raw_info['album']['title'])
            }

        elif self.type == 'album':
            search_params = {
                'album': preprocess_string(raw_info['title']),
                'artist': preprocess_string(raw_info['artist']['name'])
            }

        elif self.type == 'artist':
            search_params = {
                'artist': preprocess_string(raw_info['name'])
            }

        else:
            raise ValueError('Invalid Deezer item type')
        
        return search_params


    # TODO: Add search trials
    def search(self, search_params, _type):
        # Get the search trial list
        search_param_trials = SEARCH_PARAM_TRIALS_DICT[_type]

        # Try each search trial
        for search_trial in search_param_trials:
            # Construct the search query
            query = ''.join([f'{key}:"{value}"' for key, value in search_params.items()])
            query = quote(query)

            # Make the search request
            DEEZER_CONNECTION.request("GET", f"{DEEZER_API}search/{_type}?q={query}&order=RANKING&limit=1")
            response = DEEZER_CONNECTION.getresponse()

            # Check if the response is valid
            if response.status != 200:
                raise ValueError('Invalid response from Deezer API')
            
            # Get the response data
            data = json.loads(response.read().decode("utf-8"))

        return data



class SpotifyItem(Item):
    def __init__(self, link=None, search_params=None, item_type=None, logger=None):
        self.logger = logger

        #  Constructor from link
        #  Infer type and id from link
        #  Use id and type to get info from Spotify API
        if link:
            super().__init__(link)

            parsed_link = urlparse(self.link)
            if parsed_link.netloc != 'open.spotify.com':
                raise ValueError('Invalid Spotify link')

            # Extract the type and ID from the link path
            path_parts = parsed_link.path.split('/')
            self.type = path_parts[1]
            self.id = path_parts[2]
            self.raw_info = self.get_raw_info_from_id(self.id, self.type)
            self.search_params = self.get_search_params(self.raw_info)

        #  Constructor from search info
        #  Meaning that we want to search for the item on Spotify
        else:
            self.search_params = search_params
            self.type = item_type

            # Search for the item on Spotify and get the first result
            results = self.search()
            self.raw_info = self.get_raw_info_from_results(results, self.type)

            # Get the Spotify link from the results
            self.link = get_first_value_with_substr(self.raw_info,
                                                    'spotify',
                                                    substring=self.type)

        self.img_link = self.extract_img_link('url', 'i.scdn.co')
        self.info_simple = self.extract_info_simple(artists_key='artists', item_name_key='name')
        self.web_info = self.extract_web_info()


    def get_raw_info_from_id(self, id, _type):
        # Get the info from the Spotify API using the id and type
        if _type == 'track':
            return SPOTIFY.track(id)

        elif _type == 'album':
            return SPOTIFY.album(id)

        elif _type == 'artist':
            return SPOTIFY.artist(id)

        else:
            raise ValueError('Invalid Spotify item type')

    
    def get_raw_info_from_results(self, results, _type):
        return results[f'{_type}s']['items'][0]


    def get_search_params(self, raw_info):
        if self.type == 'track':
            search_params = {
                'track': preprocess_string(raw_info['name']),
                'artist': preprocess_string(raw_info['artists'][0]['name']),
                'album': preprocess_string(raw_info['album']['name'])
            }

        elif self.type == 'album':
            search_params = {
                'album': preprocess_string(raw_info['name']),
                'artist': preprocess_string(raw_info['artists'][0]['name'])
            }

        elif self.type == 'artist':
            search_params = {
                'artist': preprocess_string(raw_info['name'])
            }

        else:
            raise ValueError('Invalid Spotify item type')

        return search_params
    

    def search(self):
        """
        Search for a Spotify item using the search_dict and item_type.
        The search_dict is a dictionary with the following keys
        - track
        - artist
        - album
        The item_type is a string that can be either 'track', 'album' or 'artist'.
        """

        # Get the trials corresponding to the item_type
        search_params = SEARCH_PARAM_TRIALS_DICT[self.type]

        def _get_query(trial):
            """
            Get the query string from the search_dict and trial.
            The trial is a list of keys from the search_dict.
            """

            query = ''
            for key in trial:  # e.g ['track', 'artist', 'album']
                value = self.search_params[key]
                query += (f'{key}:' + value + ' ') if value is not None else ''

            if self.logger is not None:
                self.logger.info(f'Spotify query = {query}')

            return query

        found = False
        trial_index = 0
        while not found:
            if self.logger is not None:
                self.logger.info(f'Trying {search_params[trial_index]}...')

            trial = search_params[trial_index]
            spotify_query = _get_query(trial)
            spotify_results = SPOTIFY.search(
                q=spotify_query, limit=1, type=self.type)
            found = spotify_results[self.type+'s']['total'] > 0

            if not found and trial_index == len(search_params) - 1:
                error_msg = f'Could not find {self.type} in Spotify...'
                if self.logger is not None:
                    self.logger.info(error_msg)
                raise FileNotFoundError(error_msg)
            else:
                trial_index += 1

        if self.logger is not None:
            self.logger.info(f'Found {self.type} in Spotify!')
            self.logger.debug(
                f'Spotify results = {pp.pformat(spotify_results)}')

        return spotify_results


if __name__ == '__main__':
    deezer_item = DeezerItem(link='https://deezer.page.link/i91thUP4sU1CimYi6')
    pp.pprint(deezer_item.web_info)

    spotify_item = SpotifyItem(
        link='https://open.spotify.com/track/5NGBpnkXvvC1iOLByxVsRG?si=edaa77825a414659')
    pp.pprint(spotify_item.web_info)
