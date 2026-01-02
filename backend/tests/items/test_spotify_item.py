"""Tests for the SpotifyItem class."""

import pytest
from unittest.mock import Mock, patch

from spoteezer.items.spotify_item import SpotifyItem


class TestSpotifyItem:
    """Test cases for SpotifyItem class."""

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.spotify_item.SPOTIFY")
    def test_init_from_url_track(self, mock_spotify, mock_requests_get):
        """Test SpotifyItem initialization from a track URL."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Spotify API response
        mock_spotify.track.return_value = {
            "id": "4iV5W9uYEdYUVa79Axb7Rh",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}],
            "album": {
                "name": "Test Album",
                "images": [{"url": "https://example.com/cover.jpg"}],
            },
            "duration_ms": 180000,
            "external_ids": {"isrc": "USRC12345678"},
        }

        item = SpotifyItem(url="https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")

        assert item.type == "track"
        assert item.id == "4iV5W9uYEdYUVa79Axb7Rh"
        assert item.isrc == "USRC12345678"
        assert item.img_url == "https://example.com/cover.jpg"
        assert item.search_params["track"] == "test track"
        assert item.search_params["artist"] == "test artist"
        assert item.search_params["album"] == "test album"
        assert item.search_params["duration_sec"] == 180

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.spotify_item.SPOTIFY")
    def test_init_from_url_album(self, mock_spotify, mock_requests_get):
        """Test SpotifyItem initialization from an album URL."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://open.spotify.com/album/7x2nJBjbRxYc4NhLfokp5i"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Spotify API response
        mock_spotify.album.return_value = {
            "id": "7x2nJBjbRxYc4NhLfokp5i",
            "name": "Test Album",
            "artists": [{"name": "Test Artist"}],
            "images": [{"url": "https://example.com/album_cover.jpg"}],
            "tracks": {
                "items": [
                    {"name": "Track 1"},
                    {"name": "Track 2"},
                ]
            },
        }

        item = SpotifyItem(url="https://open.spotify.com/album/7x2nJBjbRxYc4NhLfokp5i")

        assert item.type == "album"
        assert item.id == "7x2nJBjbRxYc4NhLfokp5i"
        assert item.img_url == "https://example.com/album_cover.jpg"
        assert item.search_params["album"] == "test album"
        assert item.search_params["artist"] == "test artist"
        assert len(item.search_params["tracks"]) == 2

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.spotify_item.SPOTIFY")
    def test_init_from_url_artist(self, mock_spotify, mock_requests_get):
        """Test SpotifyItem initialization from an artist URL."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://open.spotify.com/artist/3Nrfpe0tUJi4K4DXYWgMUX"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Spotify API response
        mock_spotify.artist.return_value = {
            "id": "3Nrfpe0tUJi4K4DXYWgMUX",
            "name": "Test Artist",
            "images": [{"url": "https://example.com/artist_pic.jpg"}],
        }

        item = SpotifyItem(url="https://open.spotify.com/artist/3Nrfpe0tUJi4K4DXYWgMUX")

        assert item.type == "artist"
        assert item.id == "3Nrfpe0tUJi4K4DXYWgMUX"
        assert item.img_url == "https://example.com/artist_pic.jpg"
        assert item.search_params["artist"] == "test artist"

    @patch("spoteezer.items.abstract_item.requests.get")
    def test_init_from_url_invalid_domain(self, mock_requests_get):
        """Test that invalid Spotify URL domain raises ValueError."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://invalid.com/track/123"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid Spotify URL"):
            SpotifyItem(url="https://invalid.com/track/123")

    @patch("spoteezer.items.spotify_item.SPOTIFY")
    @patch("spoteezer.items.spotify_item.get_first_value_with_substr")
    def test_init_from_item_with_isrc(self, mock_get_url, mock_spotify):
        """Test SpotifyItem initialization from another item using ISRC."""
        # Mock source item
        mock_source_item = Mock()
        mock_source_item.type = "track"
        mock_source_item.isrc = "USRC12345678"
        mock_source_item.search_params = {
            "track": "test track",
            "artist": "test artist",
        }

        # Mock ISRC lookup - need full structure for get_img_url
        mock_spotify.search.return_value = {
            "tracks": {
                "total": 1,
                "items": [
                    {
                        "id": "4iV5W9uYEdYUVa79Axb7Rh",
                        "name": "Test Track",
                        "album": {
                            "images": [{"url": "https://example.com/cover.jpg"}],
                        },
                        "external_urls": {"spotify": "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"},
                    }
                ],
            }
        }
        mock_get_url.return_value = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"

        item = SpotifyItem(item=mock_source_item)

        assert item.type == "track"
        assert item.id == "4iV5W9uYEdYUVa79Axb7Rh"
        mock_spotify.search.assert_called_once_with(q="isrc:USRC12345678", type="track")

    @patch("spoteezer.items.spotify_item.SPOTIFY")
    @patch("spoteezer.items.spotify_item.get_first_value_with_substr")
    def test_init_from_item_with_search(self, mock_get_url, mock_spotify):
        """Test SpotifyItem initialization from another item using search."""
        # Mock source item
        mock_source_item = Mock()
        mock_source_item.type = "track"
        mock_source_item.isrc = None
        mock_source_item.search_params = {
            "track": "test track",
            "artist": "test artist",
            "album": "test album",
            "duration_sec": 180,
        }

        # Mock ISRC lookup (should return empty) - first call
        # Mock search - second call, need full structure for get_img_url
        def search_side_effect(*args, **kwargs):
            if "isrc:" in kwargs.get("q", ""):
                return {"tracks": {"total": 0, "items": []}}
            else:
                return {
                    "tracks": {
                        "total": 1,
                        "items": [
                            {
                                "id": "4iV5W9uYEdYUVa79Axb7Rh",
                                "name": "Test Track",
                                "album": {
                                    "images": [{"url": "https://example.com/cover.jpg"}],
                                },
                                "external_urls": {"spotify": "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"},
                            }
                        ],
                    }
                }

        mock_spotify.search.side_effect = search_side_effect
        mock_get_url.return_value = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"

        item = SpotifyItem(item=mock_source_item)

        assert item.type == "track"
        assert item.id == "4iV5W9uYEdYUVa79Axb7Rh"

    def test_preprocess_string(self):
        """Test string preprocessing removes 'with', 'feat', etc."""
        item = SpotifyItem.__new__(SpotifyItem)

        # Test with "with"
        result = item.preprocess_string("Song Title (with Artist)")
        assert result == "Song Title"

        # Test with "feat"
        result = item.preprocess_string("Song Title (feat Artist)")
        assert result == "Song Title"

        # Test with bracket
        result = item.preprocess_string("Song Title [ft Artist]")
        assert result == "Song Title"

        # Test without stop words
        result = item.preprocess_string("Clean Song Title")
        assert result == "Clean Song Title"

    def test_get_search_params_invalid_type(self):
        """Test that get_search_params raises ValueError for invalid type."""
        with patch("spoteezer.items.abstract_item.requests.get"):
            item = SpotifyItem.__new__(SpotifyItem)
            item.type = "invalid"
            item.raw_info = {}

            with pytest.raises(ValueError, match="Invalid Spotify item type"):
                item.get_search_params()

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.spotify_item.SPOTIFY")
    def test_extract_web_info(self, mock_spotify, mock_requests_get):
        """Test web info extraction."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Spotify API response
        mock_spotify.track.return_value = {
            "id": "4iV5W9uYEdYUVa79Axb7Rh",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}],
            "album": {
                "name": "Test Album",
                "images": [{"url": "https://example.com/cover.jpg"}],
            },
            "duration_ms": 180000,
            "external_ids": {"isrc": "USRC12345678"},
        }

        item = SpotifyItem(url="https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")

        web_info = item.extract_web_info()
        assert web_info["platform"] == "spotify"
        assert web_info["type"] == "track"
        assert web_info["id"] == "4iV5W9uYEdYUVa79Axb7Rh"
        assert web_info["url"] == "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        assert web_info["img_url"] == "https://example.com/cover.jpg"
