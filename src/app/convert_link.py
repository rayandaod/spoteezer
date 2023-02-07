import argparse
import pprint
import logging

from helper import *
from items.item import Item
from items.deezer_item import DeezerItem
from items.spotify_item import SpotifyItem

pp = pprint.PrettyPrinter(indent=4)


def get_item(url: str, logger=None):
    """Gets the item from the given URL.

    Args:
        URL (str): URL of the item.
        logger (Logger, optional): Logger object to log information. Defaults to None.

    Raises:
        ValueError: If the URL is not from Deezer or Spotify.

    Returns:
        Item: The item from the given URL.
    """
    if 'deezer' in url:
        item = DeezerItem(url=url, logger=logger)
    elif 'spotify' in url:
        item = SpotifyItem(url=url, logger=logger)
    else:
        raise ValueError(
            f'Could not determine between Deezer and Spotify from URL.')

    if logger is not None:
        logger.info(f'Initialized {item.PLATFORM} item from URL {url}')

    return item


def convert_item(init_item: Item, logger=None):
    """Converts the given initial item into another item,
    i.e from a DeezerItem to a SpotifyItem and vice-versa.

    Args:
        init_item (Item): The initial item to convert.
        logger (Logger, optional): Logger object to log information. Defaults to None.

    Returns:
        Item: The item from the given URL.
    """
    if type(init_item) is DeezerItem:

        return SpotifyItem(item=init_item, logger=logger)
    
    elif type(init_item) is SpotifyItem:

        return DeezerItem(item=init_item, logger=logger)

    if logger is not None:
        logger.info(
            f'Converted {init_item.PLATFORM} item to {result_item.PLATFORM} item')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('init_link', type=str)
    args = parser.parse_args()
    init_link = args.init_link

    # Initialize logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Change to logging.DEBUG for more info
    logger.addHandler(logging.StreamHandler())

    #  Creat the item from the link and convert it
    init_item = get_item(init_link, logger=logger)
    result_item = convert_item(init_item, logger=logger)

    print()
    pp.pprint(init_item.web_info)
    
    print()
    pp.pprint(result_item.web_info)
