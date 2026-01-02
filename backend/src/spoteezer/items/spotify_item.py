import re
import pprint
import structlog

from typing import Optional, Any
from urllib.parse import urlparse

from spoteezer.items.abstract_item import AbstractItem, SEARCH_PARAM_TRIALS_DICT
from spoteezer.config import SPOTIFY
from spoteezer.helper import preprocess_string, get_first_value_with_substr

PRETTY_PRINTER = pprint.PrettyPrinter(indent=4)
LOGGER: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class SpotifyItem(AbstractItem):
    PLATFORM = "spotify"

    def __init__(self, url: Optional[str] = None, item: Optional[AbstractItem] = None):
        """Constructor for the SpotifyItem class.

        Args:
            url (str, optional): The Spotify URL to the item. Defaults to None.
            item (AbstractItem, optional): The Item to copy. Defaults to None.
        """

        #  Constructor from URL
        #  Infer type and id from URL
        #  Use id and type to get info from Spotify API
        if url:
            super().__init__(url)

            parsed_url = urlparse(self.url)
            if parsed_url.netloc != "open.spotify.com":
                raise ValueError("Invalid Spotify URL")

            # Extract the type and ID from the URL path
            path_parts = parsed_url.path.split("/")
            self.type = path_parts[1]
            self.id = path_parts[2]
            self.raw_info = self.get_raw_info_from_id()
            self.search_params = self.get_search_params()
            self.img_url = self.get_img_url()
            self.web_info = self.extract_web_info()

            if self.type == "track":
                self.search_params["track"] = self.preprocess_string(
                    self.search_params["track"]
                )
                self.isrc = self.raw_info["external_ids"]["isrc"]

            if self.type in ["track", "album"]:
                self.search_params["album"] = self.preprocess_string(
                    self.search_params["album"]
                )

        #  Constructor from search info
        #  Meaning that we want to search for the item on Spotify
        elif item:
            self.type = item.type
            self.raw_info = None
            self.search_params = item.search_params

            # Get raw_info by ISRC
            if self.type == "track":
                self.isrc = item.isrc
                res = self.get_track_from_isrc()

                if res is not None and res["tracks"]["total"] != 0:
                    self.raw_info = res

            # Get raw_info by search
            if self.raw_info is None:
                res = self.search(self.search_params, self.type)
                if res is None:
                    raise FileNotFoundError("Could not find item on Spotify...")
                self.raw_info = self.get_first_raw_info(res)
            else:
                # raw_info was set from ISRC search
                pass

            # Get id, url, and web_info from raw_info
            assert self.raw_info is not None, "raw_info must be set"
            self.id = self.raw_info["id"]
            url_result = get_first_value_with_substr(
                self.raw_info, "spotify", substring=self.type
            )
            if url_result is None:
                raise ValueError("Could not extract URL from raw_info")
            self.url = url_result
            self.img_url = self.get_img_url()
            self.web_info = self.extract_web_info()

    # Remove everything after "with", "with" included, if there is a "with" in track name
    def preprocess_string(self, string: str) -> str:
        stop_words = ["with", "feat", "ft", "featuring"]

        for word in stop_words:
            parenthesis_word = f" ({word} "
            bracket_word = f" [{word} "

            if parenthesis_word in string:
                string = string[: string.index(parenthesis_word)]

            elif bracket_word in string:
                string = string[: string.index(bracket_word)]

        return string

    def get_raw_info_from_id(self) -> dict[str, Any]:
        """Gets the raw info from the Spotify API using the id and type.

        Raises:
            ValueError: If the type is invalid.

        Returns:
            dictionary: The raw info from the Spotify API.
        """
        # Get the info from the Spotify API using the id and type
        if self.type == "track":
            return SPOTIFY.track(self.id)

        elif self.type == "album":
            return SPOTIFY.album(self.id)

        elif self.type == "artist":
            return SPOTIFY.artist(self.id)

        else:
            raise ValueError("Invalid Spotify item type")

    def get_first_raw_info(self, results: dict[str, Any]) -> dict[str, Any]:
        """Gets the first item from a Spotify search results.

        Args:
            results (dictionary): The result dictionary of a Spotify search.
            _type (string): The search type (either 'track', 'album', or 'artist').

        Returns:
            dictionary: The first item from the search results.
        """
        return results[f"{self.type}s"]["items"][0]

    def get_search_params(self) -> dict[str, Any]:
        """Gets the search parameters from the raw info of the item.

        Args:
            raw_info (dictionary): The raw info of the Spotify item.

        Raises:
            ValueError: If the item type is invalid.

        Returns:
            dictionary: The search parameters for later constructing a search query.
        """
        assert self.raw_info is not None, "raw_info must be set before calling get_search_params"

        def _prep_spotify_track_name(track_name: str) -> str:
            """Preprocesses the track name.

            Returns:
                string: The preprocessed track name.
            """
            # Remove the '(feat. ...)' string from the track name
            return re.sub(r"\(feat.*\)", "", track_name)

        if self.type == "track":
            search_params = {
                "track": preprocess_string(
                    _prep_spotify_track_name(self.raw_info["name"])
                ),
                "artist": preprocess_string(self.raw_info["artists"][0]["name"]),
                "album": preprocess_string(self.raw_info["album"]["name"]),
                "duration_sec": int(self.raw_info["duration_ms"] / 1000),
            }

        elif self.type == "album":
            search_params = {
                "album": preprocess_string(self.raw_info["name"]),
                "artist": preprocess_string(self.raw_info["artists"][0]["name"]),
                "tracks": [
                    preprocess_string(track["name"])
                    for track in self.raw_info["tracks"]["items"]
                ],
            }

        elif self.type == "artist":
            search_params = {"artist": preprocess_string(self.raw_info["name"])}

        else:
            raise ValueError("Invalid Spotify item type")

        return search_params

    def get_img_url(self) -> str:
        """Gets the image url of the Spotify item.

        Returns:
            string: The image url of the Spotify item.
        """
        assert self.raw_info is not None, "raw_info must be set before calling get_img_url"
        if self.type == "track":
            return self.raw_info["album"]["images"][0]["url"]
        elif self.type == "album":
            return self.raw_info["images"][0]["url"]
        elif self.type == "artist":
            return self.raw_info["images"][0]["url"]
        else:
            raise ValueError(f"Invalid Spotify item type: {self.type}")

    def search(self, search_params: dict[str, Any], _type: str, limit: int = 1) -> dict[str, Any]:
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

            query = ""
            for key in trial:  # e.g ['track', 'artist', 'album']
                value = search_params[key]
                if key == "duration_sec":
                    # Spotify search doesn't support duration search
                    pass
                elif key == "tracks":
                    # TODO
                    pass
                else:
                    query += (f"{key}:" + str(value) + " ") if value is not None else ""
            LOGGER.info("spotify_query", query=query)

            return query

        for search_params_t in search_params_trials:
            LOGGER.info("trying_search_trial", search_trial=search_params_t, type=_type)
            query = _get_query(search_params_t)
            results = SPOTIFY.search(q=query, limit=limit, type=_type)
            found = results[_type + "s"]["total"] > 0

            if found:
                break

        if not found:
            raise FileNotFoundError("Could not find item on Spotify...")

        LOGGER.info("item_found", type=_type, platform="spotify")
        LOGGER.debug("spotify_results", results=PRETTY_PRINTER.pformat(results))
        return results

    def get_track_from_isrc(self) -> dict[str, Any] | None:
        """Gets the track info from the Spotify API using the ISRC.

        Args:
            isrc (string): The ISRC of the track.

        Returns:
            dictionary: The track info from the Spotify API.
        """

        try:
            LOGGER.info("getting_track_by_isrc", isrc=self.isrc, platform="spotify")
            return SPOTIFY.search(q=f"isrc:{self.isrc}", type="track")

        except Exception as e:
            LOGGER.warning("isrc_search_failed", isrc=self.isrc, error=str(e))
            return None
