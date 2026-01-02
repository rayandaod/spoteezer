import pprint
import structlog

from typing import Optional, Any
from urllib.parse import quote

from spoteezer.items.abstract_item import AbstractItem, SEARCH_PARAM_TRIALS_DICT
from spoteezer.config import DEEZER
from spoteezer.helper import preprocess_string

PRETTY_PRINTER = pprint.PrettyPrinter(indent=4)
LOGGER: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class DeezerItem(AbstractItem):
    PLATFORM = "deezer"
    id: int  # Override: Deezer IDs are always int

    def __init__(self, url: Optional[str] = None, item: Optional[AbstractItem] = None):
        """Instanciates a Deezer item based on the given parameter(s).

        Args:
            url (str, optional): URL to instanciate the item from. Defaults to None.
            item (Item, optional): Item to instanciate the item from. Defaults to None.
        """

        # Constructor from url
        if url:
            super().__init__(url)
            self.type = self.url.split("/")[-2]
            self.id = int(self.url.split("/")[-1].split("?")[0])
            self.raw_info = self.get_raw_info_from_id()
            self.search_params = self.get_search_params()
            self.img_url = self.get_img_url()
            self.web_info = self.extract_web_info()
            self.isrc = self.raw_info["isrc"] if self.type == "track" else None

        # Constructor from another item
        elif item:
            self.type = item.type
            self.raw_info = None
            self.search_params = item.search_params

            # Get raw_info by ISRC
            if self.type == "track":
                self.isrc = item.isrc
                res = self.get_track_from_isrc()

                if res is not None:
                    self.raw_info = res

            # Get raw_info by search
            if self.raw_info is None:
                results = self.search(self.search_params, self.type)
                self.raw_info = self.get_first_raw_info(results)

            # Get id, url, and web_info from raw_info
            assert self.raw_info is not None, "raw_info must be set"
            self.id = self.raw_info["id"]
            self.url = self.raw_info["link"]
            self.img_url = self.get_img_url()
            self.web_info = self.extract_web_info()

    def get_raw_info_from_id(self) -> dict[str, Any]:
        """Gets the raw info from the id and type of a Deezer item.

        Args:
            id (str): The Deezer item id.
            _type (str): The Deezer item type, i.e track, album, or artist.

        Returns:
            dict: The dictionary containing the raw information.
        """

        # Get the data from the Deezer API
        if self.type == "track":
            result = DEEZER.get_track(self.id)
        elif self.type == "album":
            result = DEEZER.get_album(self.id)
        elif self.type == "artist":
            result = DEEZER.get_artist(self.id)

        return result.as_dict()

    def get_first_raw_info(self, results: Any) -> dict[str, Any]:
        """Extracts raw information from search results, i.e the
        first item here.

        Args:
            results (dict): The results from a previous search.

        Returns:
            dict: The raw information from the first item in the results here.
        """
        return results[0].as_dict()

    def get_search_params(self) -> dict[str, Any]:
        """Gets the search parameters for later search, based on the given raw
        information.

        Args:
            raw_info (dict): The raw information to get the search parameters from.

        Raises:
            ValueError: If the Deezer type is not valid.

        Returns:
            dict: The search parameters issued from the raw information of the current item.
        """
        assert self.raw_info is not None, "raw_info must be set before calling get_search_params"
        if self.type == "track":
            search_params = {
                "track": preprocess_string(self.raw_info["title"]),
                "artist": preprocess_string(self.raw_info["artist"]["name"]),
                "album": preprocess_string(self.raw_info["album"]["title"]),
                "duration_sec": self.raw_info["duration"],
            }

        elif self.type == "album":
            search_params = {
                "album": preprocess_string(self.raw_info["title"]),
                "artist": preprocess_string(self.raw_info["artist"]["name"]),
                "tracks": [
                    preprocess_string(track["title"])
                    for track in self.raw_info["tracks"]
                ],
            }

        elif self.type == "artist":
            search_params = {"artist": preprocess_string(self.raw_info["name"])}

        else:
            raise ValueError("Invalid Deezer item type")

        return search_params

    def get_img_url(self) -> str:
        """Gets the image URL of the item.

        Returns:
            str: The image URL of the item.
        """
        assert self.raw_info is not None, "raw_info must be set before calling get_img_url"
        if self.type == "track":
            return self.raw_info["album"]["cover_big"]
        elif self.type == "album":
            return self.raw_info["cover_big"]
        elif self.type == "artist":
            return self.raw_info["picture_big"]
        else:
            raise ValueError(f"Invalid Deezer item type: {self.type}")

    def search(self, search_params: dict[str, Any], _type: str, limit: int = 1) -> Any:
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
            query = ""
            for key, value in search_params.items():
                if key in search_trial:
                    if key == "duration_sec":
                        query += f"dur_min:{value} dur_max:{value} "
                    elif key == "tracks":
                        pass
                    else:
                        query += f'{key}:"{value}" '
            return query

        # Try each search trial
        for search_trial in search_param_trials:
            LOGGER.info("trying_search_trial", search_trial=search_trial, type=_type)
            query = _get_query(search_trial, _type)
            LOGGER.info("deezer_query", query=query)
            query = quote(query)

            # Make the search request
            if _type == "track":
                results = DEEZER.search(query)
            elif _type == "album":
                results = DEEZER.search_albums(query)
            elif _type == "artist":
                results = DEEZER.search_artists(query)

            if len(results) > 0:
                break

        if len(results) == 0:
            raise FileNotFoundError("Could not find item on Deezer...")

        return results

    def get_track_from_isrc(self) -> dict[str, Any] | None:
        """Searches the Deezer database with the current ISRC.

        Returns:
            dict: The results obtained from the search.
        """
        try:
            return DEEZER.request("GET", f"track/isrc:{self.isrc}").as_dict()

        except Exception as e:
            LOGGER.warning("isrc_search_failed", isrc=self.isrc, error=str(e))
            return None
