import json

from http.client import HTTPSConnection

from helper import get_final_link, preprocess_string


DEEZER_API = "/2.0/"
DEEZER_CONNECTION = HTTPSConnection("api.deezer.com")


class Item():
    def __init__(self, link, start_link, logger=None):
        self.link = link
        self.start_link = start_link
        self.logger = logger
        self.check_link()
    
    def check_link(self):
        """
        Check if the link is valid.
        """

        if self.link is None:
            raise ValueError('Link is None')

        # Remove whitespace and replace http with https
        tmp_link = self.link.strip()
        tmp_link = self.link.replace('http://', 'https://')
        
        # Get the final link after redirections
        tmp_link = get_final_link(self.link, logger=self.logger)

        if tmp_link.startswith(self.start_link):
            self.link = tmp_link

        else:
            raise ValueError('Invalid link')


class DeezerItem(Item):

    def __init__(self, link, logger=None):
        super().__init__(link,
                         start_link='https://www.deezer.com/',
                         logger=logger)

        # Get the Deezer item type and id
        self.type = self.link.split('/')[-2]
        self.id = int(self.link.split('/')[-1].split('?')[0])

        if self.logger is not None:
            self.logger.info(f'Deezer item type = {self.type}')
            self.logger.info(f'Deezer item id = {self.id}')

        # Reconstruct a clean link
        link_clean = DEEZER_API + "%s/%d" % (self.type, self.id)

        if self.logger is not None:
            self.logger.info(f'Deezer link clean = {link_clean}')

        # Get the data from the Deezer API
        DEEZER_CONNECTION.request("GET", link_clean)
        response = DEEZER_CONNECTION.getresponse()
        self.info = json.loads(response.read().decode("utf-8"))


    def get_search_info(self):
        """
        Get the item info from the Deezer API.
        The support is a string that can be either 'track', 'album' or 'artist'.
        The id is the id of the item in Deezer's database.
        """

        self.search_info = {}

        if self.type == 'track':
            self.info = {
                'track': preprocess_string(self.info['title']),
                'artist': preprocess_string(self.info['artist']['name']),
                'album': preprocess_string(self.info['album']['title'])
            }

        elif self.type == 'album':
            self.info = {
                'album': preprocess_string(self.info['title']),
                'artist': preprocess_string(self.info['artist']['name'])
            }

        elif self.type == 'artist':
            self.info = {
                'artist': preprocess_string(self.info['name'])
            }

        else:
            raise ValueError('Invalid Deezer item type')

        return self.info