import structlog

from spoteezer.items.abstract_item import AbstractItem
from spoteezer.items.deezer_item import DeezerItem
from spoteezer.items.spotify_item import SpotifyItem

LOGGER: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

def get_item(url: str):
    """Gets the item from the given URL.

    Args:
        URL (str): URL of the item.

    Raises:
        ValueError: If the URL is not from Deezer or Spotify.

    Returns:
        Item: The item from the given URL.
    """
    if "deezer" in url:
        item = DeezerItem(url=url)
    elif "spotify" in url:
        item = SpotifyItem(url=url)
    else:
        raise ValueError("Could not determine between Deezer and Spotify from URL.")

    LOGGER.info("item_initialized", platform=item.PLATFORM, url=url)

    return item


def convert_item(init_item: AbstractItem):
    """Converts the given initial item into another item,
    i.e from a DeezerItem to a SpotifyItem and vice-versa.

    Args:
        init_item (AbstractItem): The initial item to convert.

    Returns:
        AbstractItem: The item from the given URL.
    """
    if type(init_item) is DeezerItem:
        result_item = SpotifyItem(item=init_item)
    elif type(init_item) is SpotifyItem:
        result_item = DeezerItem(item=init_item)
    else:
        raise ValueError(f"Unknown item type: {type(init_item)}")

    LOGGER.info(
        "item_converted",
        from_platform=init_item.PLATFORM,
        to_platform=result_item.PLATFORM,
    )

    return result_item
