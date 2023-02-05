import pprint
import requests
import re

from abc import ABC, abstractmethod
from urllib.parse import urlparse, quote
from logging import Logger

from helper import get_first_value_with_substr, preprocess_string
from config import DEEZER, SPOTIFY


pp = pprint.PrettyPrinter(indent=4)

# Search parameters dictionary
# The key is the type of the item (track, album, artist)
# The value is a list of search parameter groups, in order of priority
SEARCH_PARAM_TRIALS_DICT = {'track': [['track', 'artist', 'album', 'duration_sec'],
                                      ['track', 'artist', 'duration_sec'],
                                      ['track', 'artist', 'album'],
                                      ['track', 'duration_sec'],
                                      ['track', 'album'],
                                      ['track']],
                            'album': [['album', 'artist', 'tracks'],
                                      ['album', 'artist',
                                      'album']],
                            'artist': [['artist']]
                            }

# !!! Spotify does not allow to search for tracks by duration !!!

# TODO: Add search by UPC (for albums)

class Item(ABC):
    def __init__(self, url: str = None, item = None, logger: Logger = None):
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


    def extract_web_info(self):
        """Extracts useful information for the web interfaces.

        Args:
            item (Item): The item from which to extract the information.

        Returns:
            dict: The extracted useful information.
        """

        return {'url': self.url,
                'type': self.type,
                'id': self.id,
                'platform': self.PLATFORM}


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


    @abstractmethod
    def get_raw_info_from_id(self):
        pass


    @abstractmethod
    def get_first_raw_info(self):
        pass


    @abstractmethod
    def get_search_params(self):
        pass


    @abstractmethod
    def search(self):
        pass


    @abstractmethod
    def get_track_from_isrc(self):
        pass


class DeezerItem(Item):

    PLATFORM = 'deezer'

    def __init__(self, url: str = None, item: Item = None, logger: Logger = None):
        """Instanciates a Deezer item based on the given parameter(s).

        Args:
            url (str, optional): URL to instanciate the item from. Defaults to None.
            item (Item, optional): Item to instanciate the item from. Defaults to None.
            logger (Logger, optional): Logger to log the actions. Defaults to None.
        """
        self.logger = logger

        # Constructor from url
        if url:
            super().__init__(url)
            self.type = self.url.split('/')[-2]
            self.id = int(self.url.split('/')[-1].split('?')[0])
            self.raw_info = self.get_raw_info_from_id()
            self.search_params = self.get_search_params()
            self.web_info = self.extract_web_info()
            self.isrc = self.raw_info['isrc'] if self.type == 'track' else None

        # Constructor from another item
        elif item:
            self.type = item.type
            self.raw_info = None
            self.search_params = item.search_params

            # Get raw_info by ISRC
            if self.type == 'track':
                self.isrc = item.isrc
                res = self.get_track_from_isrc()

                if res is not None:
                    self.raw_info = res
            
            # Get raw_info by search
            if self.raw_info is None:
                results = self.search(self.search_params, self.type)
                self.raw_info = self.get_first_raw_info(results)
            
            # Get id, url, and web_info from raw_info
            self.id = self.raw_info['id']
            self.url = self.raw_info['link']
            self.web_info = self.extract_web_info()


    def get_raw_info_from_id(self):
        """Gets the raw info from the id and type of a Deezer item.

        Args:
            id (str): The Deezer item id.
            _type (str): The Deezer item type, i.e track, album, or artist.

        Returns:
            dict: The dictionary containing the raw information.
        """

        # Get the data from the Deezer API
        if self.type == 'track':
            result = DEEZER.get_track(self.id)
        elif self.type == 'album':
            result = DEEZER.get_album(self.id)
        elif self.type == 'artist':
            result = DEEZER.get_artist(self.id)

        return result.as_dict()

    def get_first_raw_info(self, results):
        """Extracts raw information from search results, i.e the
        first item here.

        Args:
            results (dict): The results from a previous search.

        Returns:
            dict: The raw information from the first item in the results here.
        """
        return results[0].as_dict()

    def get_search_params(self):
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
                'track': preprocess_string(self.raw_info['title']),
                'artist': preprocess_string(self.raw_info['artist']['name']),
                'album': preprocess_string(self.raw_info['album']['title']),
                'duration_sec': self.raw_info['duration'],
            }

        elif self.type == 'album':
            search_params = {
                'album': preprocess_string(self.raw_info['title']),
                'artist': preprocess_string(self.raw_info['artist']['name']),
                'tracks' : [preprocess_string(track['title']) for track in self.raw_info['tracks']]
            }

        elif self.type == 'artist':
            search_params = {
                'artist': preprocess_string(self.raw_info['name'])
            }

        else:
            raise ValueError('Invalid Deezer item type')

        return search_params


    def search(self, search_params, _type, limit=1):
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

        def _get_query(search_trial, _type):
            query = ''
            for key, value in search_params.items():
                if key in search_trial:
                    if key == 'duration_sec':
                        query += f'dur_min:{value} dur_max:{value} '
                    elif key == 'tracks':
                        pass
                    else:
                        query += f'{key}:"{value}" '
            return query

        # Try each search trial
        for search_trial in search_param_trials:
            self.log(f'Trying {search_trial}...')
            query = _get_query(search_trial, _type)
            self.log(f'Deezer query: {query}')
            query = quote(query)

            # Make the search request
            if _type == 'track':
                results = DEEZER.search(query)
            elif _type == 'album':
                results = DEEZER.search_albums(query)
            elif _type == 'artist':
                results = DEEZER.search_artists(query)

            if len(results) > 0:
                break
            
        if len(results) == 0:
            raise FileNotFoundError('Could not find item on Deezer...')

        return results


    def get_track_from_isrc(self):
        """Searches the Deezer database with the current ISRC.

        Returns:
            dict: The results obtained from the search.
        """
        try:
            return DEEZER.request('GET', f'track/isrc:{self.isrc}').as_dict()

        except:
            self.log(f'Could not find track with ISRC {self.isrc} on Deezer...')
            return None



class  SpotifyItem(Item):

    PLATFORM = 'spotify'

    def __init__(self, url: str = None, item: Item = None, logger=None):
        """Constructor for the SpotifyItem class.

        Args:
            url (str, optional): The Spotify URL to the item. Defaults to None.
            item (Item, optional): The Item to copy. Defaults to None.
            logger (Logger, optional): The logger to use. Defaults to None.
        """

        self.logger = logger

        #  Constructor from URL
        #  Infer type and id from URL
        #  Use id and type to get info from Spotify API
        if url:
            super().__init__(url)

            parsed_url = urlparse(self.url)
            if parsed_url.netloc != 'open.spotify.com':
                raise ValueError('Invalid Spotify URL')

            # Extract the type and ID from the URL path
            path_parts = parsed_url.path.split('/')
            self.type = path_parts[1]
            self.id = path_parts[2]
            self.raw_info = self.get_raw_info_from_id()
            self.search_params = self.get_search_params()
            self.web_info = self.extract_web_info()

            if self.type == 'track':
                self.search_params['track'] = self.preprocess_string(self.search_params['track'])
                self.isrc = self.raw_info['external_ids']['isrc']

            if self.type in ['track', 'album']:
                self.search_params['album'] = self.preprocess_string(self.search_params['album'])

        #  Constructor from search info
        #  Meaning that we want to search for the item on Spotify
        elif item:
            self.type = item.type
            self.raw_info = None
            self.search_params = item.search_params

            # Get raw_info by ISRC
            if self.type == 'track':
                self.isrc = item.isrc
                res = self.get_track_from_isrc()

                if res is not None and res['tracks']['total'] != 0:
                    self.raw_info = res
            
            # Get raw_info by search
            if self.raw_info is None:
                res = self.search(self.search_params, self.type)
            
            # Get id, url, and web_info from raw_info
            self.raw_info = self.get_first_raw_info(res)
            self.id = self.raw_info['id']
            self.url = get_first_value_with_substr(self.raw_info, 'spotify', substring=self.type)
            self.web_info = self.extract_web_info()

    # Remove everything after "with", "with" included, if there is a "with" in track name
    def preprocess_string(self, string):
        stop_words = ['with', 'feat', 'ft', 'featuring']
        
        for word in stop_words:
            parenthesis_word = f'({word} '
            bracket_word = f'[{word} '

            if parenthesis_word in string:
                string = string[:string.index(parenthesis_word)]

            elif bracket_word in string:
                string = string[:string.index(bracket_word)]
        
        return string

    def get_raw_info_from_id(self):
        """Gets the raw info from the Spotify API using the id and type.

        Raises:
            ValueError: If the type is invalid.

        Returns:
            dictionary: The raw info from the Spotify API.
        """
        # Get the info from the Spotify API using the id and type
        if self.type == 'track':
            return SPOTIFY.track(self.id)

        elif self.type == 'album':
            return SPOTIFY.album(self.id)

        elif self.type == 'artist':
            return SPOTIFY.artist(self.id)

        else:
            raise ValueError('Invalid Spotify item type')

    def get_first_raw_info(self, results):
        """Gets the first item from a Spotify search results.

        Args:
            results (dictionary): The result dictionary of a Spotify search.
            _type (string): The search type (either 'track', 'album', or 'artist').

        Returns:
            dictionary: The first item from the search results.
        """
        return results[f'{self.type}s']['items'][0]

    def get_search_params(self):
        """Gets the search parameters from the raw info of the item.

        Args:
            raw_info (dictionary): The raw info of the Spotify item.

        Raises:
            ValueError: If the item type is invalid.

        Returns:
            dictionary: The search parameters for later constructing a search query.
        """

        def _prep_spotify_track_name(track_name):
            """Preprocesses the track name.

            Returns:
                string: The preprocessed track name.
            """
            # Remove the '(feat. ...)' string from the track name
            return re.sub(r'\(feat.*\)', '', track_name)

        if self.type == 'track':
            search_params = {
                'track': preprocess_string(_prep_spotify_track_name(self.raw_info['name'])),
                'artist': preprocess_string(self.raw_info['artists'][0]['name']),
                'album': preprocess_string(self.raw_info['album']['name']),
                'duration_sec': int(self.raw_info['duration_ms'] / 1000)
            }

        elif self.type == 'album':
            search_params = {
                'album': preprocess_string(self.raw_info['name']),
                'artist': preprocess_string(self.raw_info['artists'][0]['name']),
                'tracks': [preprocess_string(track['name']) for track in self.raw_info['tracks']['items']]
            }

        elif self.type == 'artist':
            search_params = {
                'artist': preprocess_string(self.raw_info['name'])
            }

        else:
            raise ValueError('Invalid Spotify item type')

        return search_params

    def search(self, search_params, _type, limit=1):
        """Searches for the item on Spotify.

        Raises:
            FileNotFoundError: If the search parameters are invalid.

        Returns:
            dict: The search results.
        """

        # Get the trials corresponding to the item_type
        search_params_trials = SEARCH_PARAM_TRIALS_DICT[_type]

        def _get_query(trial):
            """Generates the query from the current search trial and
            the search params of the current SpotifyItem object.

            Args:
                trial (list): List of keys to process in the query

            Returns:
                str: The final query for that search parameters trial.
            """

            query = ''
            for key in trial:  # e.g ['track', 'artist', 'album']
                value = search_params[key]
                if key == 'duration_sec':
                    # Spotify search doesn't support duration search
                    pass
                elif key == 'tracks':
                    # TODO
                    pass
                else:
                    query += (f'{key}:' + str(value) + ' ') if value is not None else ''
            self.log(f'Spotify query = {query}')

            return query

        for search_params_t in search_params_trials:
            self.log(f'Trying {search_params_t}...')
            query = _get_query(search_params_t)
            results = SPOTIFY.search(q=query, limit=limit, type=_type)
            found = results[_type+'s']['total'] > 0

            if found:
                break
        
        if not found:
            raise FileNotFoundError('Could not find item on Spotify...')
        
        self.log(f'Found {_type} in Spotify!')
        self.log(
            f'Spotify results = {pp.pformat(results)}', level='debug')
        return results

    def get_track_from_isrc(self):
        """Gets the track info from the Spotify API using the ISRC.

        Args:
            isrc (string): The ISRC of the track.

        Returns:
            dictionary: The track info from the Spotify API.
        """

        try:
            self.log(f'Getting track with ISRC {self.isrc} from Spotify...')
            return SPOTIFY.search(q=f'isrc:{self.isrc}', type='track')

        except:
            self.log(f'Could not find track with ISRC {self.isrc} on Deezer...')
            return None


if __name__ == '__main__':
    deezer_item = DeezerItem(url='https://deezer.page.link/i91thUP4sU1CimYi6')
    pp.pprint(deezer_item.web_info)

    spotify_item = SpotifyItem(
        url='https://open.spotify.com/track/5NGBpnkXvvC1iOLByxVsRG?si=edaa77825a414659')
    pp.pprint(spotify_item.web_info)
