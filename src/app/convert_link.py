import argparse
import pprint
import logging

from helper import *
from items import DeezerItem, Item, SpotifyItem

pp = pprint.PrettyPrinter(indent=4)


def get_init_item(link, logger=None):
    if 'deezer' in link:
        item = DeezerItem(link=link, logger=logger)
        platform = 'Deezer'
    elif 'spotify' in link:
        item = SpotifyItem(link=link, logger=logger)
        platform = 'Spotify'
    else:
        raise ValueError(
            f'Could not determine between Deezer and Spotify from link {link}...')

    return item, platform


def convert_item(init_item: Item, logger=None):
    if type(init_item) == DeezerItem:
        item = SpotifyItem(search_params=init_item.search_params, item_type=init_item.type, logger=logger)
        platform = 'Spotify'
    elif type(init_item) == SpotifyItem:
        item = DeezerItem(search_params=init_item.search_params, item_type=init_item.type, logger=logger)
        platform = 'Deezer'

    return item, platform


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('init_link', type=str)
    args = parser.parse_args()
    init_link = args.init_link

    # Initialize logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Change to logging.DEBUG for more info
    logger.addHandler(logging.StreamHandler())

    # Creat the item from the link and convert it
    init_item, init_platform = get_init_item(init_link, logger=logger)
    result_item, result_platform = convert_item(init_item, logger=logger)

    print()
    print(init_platform)
    pp.pprint(init_item.web_info)
    print()
    print(result_platform)
    pp.pprint(result_item.web_info)
