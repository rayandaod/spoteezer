"""Tests for the DeezerItem class."""

import pytest
from unittest.mock import Mock, patch

from spoteezer.items.deezer_item import DeezerItem


class TestDeezerItem:
    """Test cases for DeezerItem class."""

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.deezer_item.DEEZER")
    def test_init_from_url_track(self, mock_deezer, mock_requests_get):
        """Test DeezerItem initialization from a track URL."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://www.deezer.com/track/123456"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Deezer API response
        mock_track = Mock()
        mock_track.as_dict.return_value = {
            "id": 123456,
            "title": "Test Track",
            "artist": {"name": "Test Artist"},
            "album": {"title": "Test Album", "cover_big": "https://example.com/cover.jpg"},
            "duration": 180,
            "isrc": "USRC12345678",
            "link": "https://www.deezer.com/track/123456",
        }
        mock_deezer.get_track.return_value = mock_track

        item = DeezerItem(url="https://www.deezer.com/track/123456")

        assert item.type == "track"
        assert item.id == 123456
        assert item.url == "https://www.deezer.com/track/123456"
        assert item.isrc == "USRC12345678"
        assert item.img_url == "https://example.com/cover.jpg"
        assert item.search_params["track"] == "test track"
        assert item.search_params["artist"] == "test artist"
        assert item.search_params["album"] == "test album"
        assert item.search_params["duration_sec"] == 180

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.deezer_item.DEEZER")
    def test_init_from_url_album(self, mock_deezer, mock_requests_get):
        """Test DeezerItem initialization from an album URL."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://www.deezer.com/album/789012"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Deezer API response
        mock_album = Mock()
        mock_album.as_dict.return_value = {
            "id": 789012,
            "title": "Test Album",
            "artist": {"name": "Test Artist"},
            "cover_big": "https://example.com/album_cover.jpg",
            "tracks": [
                {"title": "Track 1"},
                {"title": "Track 2"},
            ],
        }
        mock_deezer.get_album.return_value = mock_album

        item = DeezerItem(url="https://www.deezer.com/album/789012")

        assert item.type == "album"
        assert item.id == 789012
        assert item.img_url == "https://example.com/album_cover.jpg"
        assert item.search_params["album"] == "test album"
        assert item.search_params["artist"] == "test artist"
        assert len(item.search_params["tracks"]) == 2

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.deezer_item.DEEZER")
    def test_init_from_url_artist(self, mock_deezer, mock_requests_get):
        """Test DeezerItem initialization from an artist URL."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://www.deezer.com/artist/345678"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Deezer API response
        mock_artist = Mock()
        mock_artist.as_dict.return_value = {
            "id": 345678,
            "name": "Test Artist",
            "picture_big": "https://example.com/artist_pic.jpg",
        }
        mock_deezer.get_artist.return_value = mock_artist

        item = DeezerItem(url="https://www.deezer.com/artist/345678")

        assert item.type == "artist"
        assert item.id == 345678
        assert item.img_url == "https://example.com/artist_pic.jpg"
        assert item.search_params["artist"] == "test artist"

    @patch("spoteezer.items.deezer_item.DEEZER")
    def test_init_from_item_with_isrc(self, mock_deezer):
        """Test DeezerItem initialization from another item using ISRC."""
        # Mock source item
        mock_source_item = Mock()
        mock_source_item.type = "track"
        mock_source_item.isrc = "USRC12345678"
        mock_source_item.search_params = {
            "track": "test track",
            "artist": "test artist",
        }

        # Mock ISRC lookup
        mock_isrc_track = Mock()
        mock_isrc_track.as_dict.return_value = {
            "id": 123456,
            "title": "Test Track",
            "artist": {"name": "Test Artist"},
            "album": {"title": "Test Album", "cover_big": "https://example.com/cover.jpg"},
            "duration": 180,
            "link": "https://www.deezer.com/track/123456",
        }
        mock_deezer.request.return_value = mock_isrc_track

        item = DeezerItem(item=mock_source_item)

        assert item.type == "track"
        assert item.id == 123456
        assert item.url == "https://www.deezer.com/track/123456"
        mock_deezer.request.assert_called_once_with("GET", "track/isrc:USRC12345678")

    @patch("spoteezer.items.deezer_item.DEEZER")
    def test_init_from_item_with_search(self, mock_deezer):
        """Test DeezerItem initialization from another item using search."""
        # Mock source item
        mock_source_item = Mock()
        mock_source_item.type = "track"
        mock_source_item.isrc = None
        mock_source_item.search_params = {
            "track": "test track",
            "artist": "test artist",
        }

        # Mock ISRC lookup (should return None)
        mock_deezer.request.side_effect = Exception("ISRC not found")

        # Mock search
        mock_search_result = Mock()
        mock_search_result.as_dict.return_value = {
            "id": 123456,
            "title": "Test Track",
            "artist": {"name": "Test Artist"},
            "album": {"title": "Test Album", "cover_big": "https://example.com/cover.jpg"},
            "duration": 180,
            "link": "https://www.deezer.com/track/123456",
        }
        mock_deezer.search.return_value = [mock_search_result]

        item = DeezerItem(item=mock_source_item)

        assert item.type == "track"
        assert item.id == 123456
        assert mock_deezer.search.called

    def test_get_search_params_invalid_type(self):
        """Test that get_search_params raises ValueError for invalid type."""
        with patch("spoteezer.items.abstract_item.requests.get"):
            item = DeezerItem.__new__(DeezerItem)
            item.type = "invalid"
            item.raw_info = {}

            with pytest.raises(ValueError, match="Invalid Deezer item type"):
                item.get_search_params()

    @patch("spoteezer.items.abstract_item.requests.get")
    @patch("spoteezer.items.deezer_item.DEEZER")
    def test_extract_web_info(self, mock_deezer, mock_requests_get):
        """Test web info extraction."""
        # Mock URL resolution
        mock_response = Mock()
        mock_response.url = "https://www.deezer.com/track/123456"
        mock_response.history = []
        mock_requests_get.return_value = mock_response

        # Mock Deezer API response
        mock_track = Mock()
        mock_track.as_dict.return_value = {
            "id": 123456,
            "title": "Test Track",
            "artist": {"name": "Test Artist"},
            "album": {"title": "Test Album", "cover_big": "https://example.com/cover.jpg"},
            "duration": 180,
            "isrc": "USRC12345678",
            "link": "https://www.deezer.com/track/123456",
        }
        mock_deezer.get_track.return_value = mock_track

        item = DeezerItem(url="https://www.deezer.com/track/123456")

        web_info = item.extract_web_info()
        assert web_info["platform"] == "deezer"
        assert web_info["type"] == "track"
        assert web_info["id"] == 123456
        assert web_info["url"] == "https://www.deezer.com/track/123456"
        assert web_info["img_url"] == "https://example.com/cover.jpg"
