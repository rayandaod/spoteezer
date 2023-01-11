import json
import pprint
import requests

from urllib.parse import urlparse, quote

from helper import get_first_value_with_substr, preprocess_string, extract_web_info
from config import DEEZER_CONNECTION, DEEZER_API, SPOTIFY


pp = pprint.PrettyPrinter(indent=4)

# Search parameters dictionary
# The key is the type of the item (track, album, artist)
# The value is a list of search parameter groups, in order of priority
SEARCH_PARAM_TRIALS_DICT = {'track': [['track', 'artist', 'album'],
                                      ['track', 'artist'],
                                      ['track']],
                            'album': [['album', 'artist'],
                                      ['album']],
                            'artist': [['artist']]
                            }


class Item():
    def __init__(self, url):
        """Instantiates an Item object given an URL.

        Args:
            url (str): The URL to instanciate the Item object from.

        Raises:
            ValueError: If the URL was not specified.
        """
        # Check if the url is valid
        if url is None:
            raise ValueError('URL is None')

        # Remove whitespace and replace http with https
        tmp_url = url.strip()
        tmp_url = url.replace('http://', 'https://')

        # Get the final URL after redirections
        responses = requests.get(tmp_url)
        if len(responses.history) > 0:
            self.url = responses.history[-1].url
        else:
            self.url = responses.url

    def extract_info_simple(self, artists_key=None, item_name_key=None):
        """Extracts basic information about the item.

        Args:
            artists_key (str, optional): Key to get the artists. Defaults to None.
            item_name_key (str, optional): Key to get the item name. Defaults to None.

        Returns:
            dict: Basic information extracted, e.g track name, album name, artist name.
        """

        # Initialize the info dictionary
        info_simple = {}

        # Get the artist or artists
        def _get_artists(info_simple, raw_info, artists_key):

            # Special case for Deezer (not perfect implementation for now lmao)
            if type(self) == DeezerItem and artists_key not in raw_info:
                artists_key = 'artist'

            if type(raw_info[artists_key]) == list and len(raw_info[artists_key]) > 1:
                info_simple['artists'] = ', '.join(
                    [raw_info[artists_key][i]['name'] for i in range(len(raw_info[artists_key]))])
            else:
                info_simple['artist'] = raw_info[artists_key][0]['name'] if type(
                    raw_info[artists_key]) == list else raw_info[artists_key]['name']
            return info_simple

        if self.type in ['track', 'album']:
            info_simple[self.type] = self.raw_info[item_name_key]
            info_simple = _get_artists(info_simple, self.raw_info, artists_key)

            if self.type == 'track':
                info_simple['album'] = self.raw_info['album'][item_name_key]

        elif self.type == 'artist':
            if type(self) == DeezerItem:
                info_simple['artist'] = self.raw_info['name']
            else:
                info_simple['artist'] = self.raw_info['name']

        return info_simple

    def log(self, log_str, level='info'):
        """Logs the given string in the right level and by checking if
        logger is not None first. Improves readability in the code (imo).

        Args:
            log_str (str): The string to log.
            level (str, optional): The level to log the string. Defaults to 'info'.
        """
        if self.logger is not None:
            if level == 'info':
                self.logger.info(log_str)
            elif level == 'warning':
                self.logger.warning(log_str)
            elif level == 'error':
                self.logger.error(log_str)
        else:
            print(log_str)


class DeezerItem(Item):

    PLATFORM = 'deezer'

    def __init__(self, url=None, search_params=None, item_type=None, logger=None):
        """Instanciates a Deezer item based on the given parameter(s).

        Args:
            url (str, optional): URL to instanciate the item from. Defaults to None.
            search_params (dict, optional): Search parameters to instantiate the item from,
            by searching the Deezer database and finding the closest match. Defaults to None.
            item_type (str, optional): Item type, i.e track, album, or artist. Defaults to None.
            logger (Logger, optional): The logger to log information. Defaults to None.
        """
        self.logger = logger

        # Constructor from url
        if url is not None:
            super().__init__(url)
            self.type = self.url.split('/')[-2]
            self.id = int(self.url.split('/')[-1].split('?')[0])
            self.raw_info = self.get_raw_info_from_id(self.id, self.type)
            self.search_params = self.get_search_params(self.raw_info)

        # Constructor from search parameters
        elif search_params is not None:
            self.search_params = search_params
            self.type = item_type
            results = self.search(self.search_params, self.type)
            self.raw_info = self.get_raw_info_from_results(results)
            self.id = self.raw_info['id']
            self.url = self.raw_info['link']

        self.web_info = extract_web_info(self)


    def get_raw_info_from_id(self, id, _type):
        """Gets the raw info from the id and type of a Deezer item.

        Args:
            id (str): The Deezer item id.
            _type (str): The Deezer item type, i.e track, album, or artist.

        Raises:
            ValueError: If the Deezer API sends a bad response.

        Returns:
            JSON: The JSON response from the Deezer API.
        """
        clean_url = DEEZER_API + f"{_type}/{id}"

        # Get the data from the Deezer API
        DEEZER_CONNECTION.request("GET", clean_url)
        response = DEEZER_CONNECTION.getresponse()

        # Check if the response is valid
        if response.status != 200:
            raise ValueError('Invalid response from Deezer API')

        return json.loads(response.read().decode("utf-8"))

    def get_raw_info_from_results(self, results):
        """Extracts raw information from search results, i.e the
        first item here.

        Args:
            results (dict): The results from a previous search.

        Returns:
            dict: The raw information from the first item in the results here.
        """
        return results['data'][0]

    def get_search_params(self, raw_info):
        """Gets the search parameters for later search, based on the given raw
        information.

        Args:
            raw_info (dict): The raw information to get the search parameters from.

        Raises:
            ValueError: If the Deezer type is not valid.

        Returns:
            dict: The search parameters issued from the raw information of the current item.
        """
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
        """Searches the Deeezer database with the given search parameters.
        Tries search parameter combinations by decreasing order of precision,
        according to the SEARCH_PARAM_TRIALS_DICT dictionary.

        Args:
            search_params (dict): The search parameters to search with.
            _type (str): The Deezer item type, i.e track, album, or artist. 

        Raises:
            ValueError: If the Deezer API responses with a bad status code.

        Returns:
            dict: The results obtained from the search.
        """
        # Get the search trial list
        search_param_trials = SEARCH_PARAM_TRIALS_DICT[_type]

        # Try each search trial
        for search_trial in search_param_trials:
            # Construct the search query
            query = ''.join([f'{key}:"{value}"' for key,
                            value in search_params.items()])
            query = quote(query)

            # Make the search request
            DEEZER_CONNECTION.request(
                "GET", f"{DEEZER_API}search/{_type}?q={query}&order=RANKING&limit=1")
            response = DEEZER_CONNECTION.getresponse()

            # Check if the response is valid
            if response.status != 200:
                raise ValueError('Invalid response from Deezer API')

            # Get the response data
            results = json.loads(response.read().decode("utf-8"))

        return results


class SpotifyItem(Item):

    PLATFORM = 'spotify'

    def __init__(self, URL=None, search_params=None, item_type=None, logger=None):
        """Constructor for the SpotifyItem class.

        Args:
            URL (str, optional): The Spotify URL to the item. Defaults to None.
            search_params (dict, optional): The search parameters to search with. Defaults to None.
            item_type (str, optional): The Spotify item type, i.e track, album, or artist. Defaults to None.
            logger (Logger, optional): The logger to use. Defaults to None.
        """

        self.logger = logger

        #  Constructor from URL
        #  Infer type and id from URL
        #  Use id and type to get info from Spotify API
        if URL:
            super().__init__(URL)

            parsed_url = urlparse(self.url)
            if parsed_url.netloc != 'open.spotify.com':
                raise ValueError('Invalid Spotify URL')

            # Extract the type and ID from the URL path
            path_parts = parsed_url.path.split('/')
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

            # Get the Spotify URL from the results
            self.url = get_first_value_with_substr(self.raw_info,
                                                    'spotify',
                                                    substring=self.type)

            self.id = self.raw_info['id']

        self.web_info = extract_web_info(self)

    def get_raw_info_from_id(self, id, _type):
        """Gets the raw info from the Spotify API using the id and type.

        Args:
            id (string): The Spotify id of the item.
            _type (string): The type of the item (either 'track', 'album', or 'artist').

        Raises:
            ValueError: If the type is invalid.

        Returns:
            dictionary: The raw info from the Spotify API.
        """
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
        """Gets the first item from a Spotify search results.

        Args:
            results (dictionary): The result dictionary of a Spotify search.
            _type (string): The search type (either 'track', 'album', or 'artist').

        Returns:
            dictionary: The first item from the search results.
        """
        return results[f'{_type}s']['items'][0]

    def get_search_params(self, raw_info):
        """Gets the search parameters from the raw info of the item.

        Args:
            raw_info (dictionary): The raw info of the Spotify item.

        Raises:
            ValueError: If the item type is invalid.

        Returns:
            dictionary: The search parameters for later constructing a search query.
        """

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
        """Searches for the item on Spotify.

        Raises:
            FileNotFoundError: If the search parameters are invalid.

        Returns:
            dict: The search results.
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
            self.log(f'Spotify query = {query}')

            return query

        found = False
        trial_index = 0
        while not found:
            self.log(f'Trying {search_params[trial_index]}...')

            trial = search_params[trial_index]
            spotify_query = _get_query(trial)
            spotify_results = SPOTIFY.search(
                q=spotify_query, limit=1, type=self.type)
            found = spotify_results[self.type+'s']['total'] > 0

            # If not found and we have tried all the trials
            # Return an error saying that the item was not found
            if not found and trial_index == len(search_params) - 1:
                error_msg = f'Could not find {self.type} in Spotify...'
                self.log(error_msg)
                raise FileNotFoundError(error_msg)

            # Otherwise, try the next trial
            else:
                trial_index += 1

        # If we reached this point, it means that we found the item
        # Log the results and return them
        self.log(f'Found {self.type} in Spotify!')
        self.log(
            f'Spotify results = {pp.pformat(spotify_results)}', level='debug')
        return spotify_results


if __name__ == '__main__':
    deezer_item = DeezerItem(url='https://deezer.page.link/i91thUP4sU1CimYi6')
    pp.pprint(deezer_item.web_info)

    spotify_item = SpotifyItem(
        URL='https://open.spotify.com/track/5NGBpnkXvvC1iOLByxVsRG?si=edaa77825a414659')
    pp.pprint(spotify_item.web_info)
