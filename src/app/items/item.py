import pprint
import requests

from abc import ABC, abstractmethod
from logging import Logger

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
                'platform': self.PLATFORM,
                'img_url': self.img_url}

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
    def get_img_url(self):
        pass

    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def get_track_from_isrc(self):
        pass