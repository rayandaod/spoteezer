import pprint
import requests
import structlog

from abc import ABC, abstractmethod
from typing import Optional, Any

PRETTY_PRINTER = pprint.PrettyPrinter(indent=4)
LOGGER: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

# Search parameters dictionary
# The key is the type of the item (track, album, artist)
# The value is a list of search parameter groups, in order of priority
# !!! Spotify does not allow to search for tracks by duration !!!
# TODO: Add search by UPC (for albums)
SEARCH_PARAM_TRIALS_DICT = {
    "track": [
        ["track", "artist", "album", "duration_sec"],
        ["track", "artist", "duration_sec"],
        ["track", "artist", "album"],
        ["track", "duration_sec"],
        ["track", "album"],
        ["track"],
    ],
    "album": [["album", "artist", "tracks"], ["album", "artist", "album"]],
    "artist": [["artist"]],
}


class AbstractItem(ABC):
    PLATFORM: str
    url: str
    type: str
    id: str | int
    raw_info: dict[str, Any] | None
    search_params: dict[str, Any]
    img_url: str
    isrc: str | None

    def __init__(self, url: Optional[str] = None, item: Optional["AbstractItem"] = None):
        """Instantiates an Item object given an URL.

        Args:
            url (str): The URL to instanciate the Item object from.

        Raises:
            ValueError: If the URL was not specified.
        """
        # Check if the url is valid
        if url is None:
            raise ValueError("URL is None")

        # Remove whitespace and replace http with https
        tmp_url = url.strip()
        tmp_url = url.replace("http://", "https://")

        # Get the final URL after redirections
        responses = requests.get(tmp_url)
        if len(responses.history) > 0:
            self.url = responses.history[-1].url
        else:
            self.url = responses.url

    def extract_web_info(self) -> dict[str, Any]:
        """Extracts useful information for the web interfaces.

        Args:
            item (Item): The item from which to extract the information.

        Returns:
            dict: The extracted useful information.
        """

        return {
            "url": self.url,
            "type": self.type,
            "id": self.id,
            "platform": self.PLATFORM,
            "img_url": self.img_url,
        }

    @abstractmethod
    def get_raw_info_from_id(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_first_raw_info(self, results: Any) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_search_params(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_img_url(self) -> str:
        pass

    @abstractmethod
    def search(self, search_params: dict[str, Any], _type: str, limit: int = 1) -> Any:
        pass

    @abstractmethod
    def get_track_from_isrc(self) -> dict[str, Any] | None:
        pass
