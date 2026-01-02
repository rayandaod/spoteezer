"""Live integration tests that make actual API calls to Spotify and Deezer.

These tests are skipped by default as they require:
- Valid API credentials
- Network access
- Actual API calls that may be rate-limited
"""

import pytest
from spoteezer.convert_link import get_item, convert_item


@pytest.mark.live
def test_convert_spotify_to_deezer_live():
    """Test converting a Spotify track to Deezer with actual API calls."""
    # Using a well-known track: "Blinding Lights" by The Weeknd
    spotify_url = "https://open.spotify.com/track/45dmhJngghAsnQxYSW0YaU"
    
    # Get the Spotify item
    spotify_item = get_item(spotify_url)
    assert spotify_item.PLATFORM == "spotify"
    assert spotify_item.type == "track"
    assert spotify_item.web_info is not None
    
    # Convert to Deezer
    deezer_item = convert_item(spotify_item)
    assert deezer_item.PLATFORM == "deezer"
    assert deezer_item.type == "track"
    assert deezer_item.web_info is not None
    assert deezer_item.web_info["url"] is not None


@pytest.mark.live
def test_convert_deezer_to_spotify_live():
    """Test converting a Deezer track to Spotify with actual API calls."""
    # Using a well-known track: "Blinding Lights" by The Weeknd
    deezer_url = "https://www.deezer.com/track/3135556"
    
    # Get the Deezer item
    deezer_item = get_item(deezer_url)
    assert deezer_item.PLATFORM == "deezer"
    assert deezer_item.type == "track"
    assert deezer_item.web_info is not None
    
    # Convert to Spotify
    spotify_item = convert_item(deezer_item)
    assert spotify_item.PLATFORM == "spotify"
    assert spotify_item.type == "track"
    assert spotify_item.web_info is not None
    assert spotify_item.web_info["url"] is not None


@pytest.mark.live
def test_convert_custom_url_live(test_url):
    """Test converting a custom URL provided via --url option."""
    if test_url is None:
        pytest.skip("No URL provided via --url option")
    
    # Get the item from the provided URL
    item = get_item(test_url)
    assert item.web_info is not None
    
    # Convert to the other platform
    converted_item = convert_item(item)
    assert converted_item.PLATFORM != item.PLATFORM
    assert converted_item.type == item.type
    assert converted_item.web_info is not None
    assert converted_item.web_info["url"] is not None
