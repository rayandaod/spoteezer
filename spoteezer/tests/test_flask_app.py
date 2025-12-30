"""Simple test to ensure the Flask app works as expected."""

import pytest
from unittest.mock import Mock, patch
from spoteezer.flask_app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_convert_endpoint_success(client):
    """Test that the /convert endpoint works correctly with a valid request."""
    # Mock the item objects
    mock_init_item = Mock()
    mock_init_item.web_info = {
        "url": "https://open.spotify.com/track/test123",
        "type": "track",
        "id": "test123",
        "platform": "spotify",
        "img_url": "https://example.com/image.jpg",
    }

    mock_result_item = Mock()
    mock_result_item.web_info = {
        "url": "https://www.deezer.com/track/test456",
        "type": "track",
        "id": "test456",
        "platform": "deezer",
        "img_url": "https://example.com/image2.jpg",
    }

    # Mock the conversion functions
    with (
        patch("spoteezer.flask_app.get_item", return_value=mock_init_item),
        patch("spoteezer.flask_app.convert_item", return_value=mock_result_item),
    ):
        # Make a POST request to the /convert endpoint
        response = client.post(
            "/convert",
            json={"initURL": "https://open.spotify.com/track/test123"},
            content_type="application/json",
        )

        # Assert the response
        assert response.status_code == 200
        data = response.get_json()
        assert "result" in data
        assert "log" in data
        assert data["log"] == "Conversion successful!"
        assert "init" in data["result"]
        assert "result" in data["result"]
        assert data["result"]["init"]["platform"] == "spotify"
        assert data["result"]["result"]["platform"] == "deezer"


def test_convert_endpoint_missing_url(client):
    """Test that the /convert endpoint handles missing URL gracefully."""
    response = client.post("/convert", json={}, content_type="application/json")

    assert response.status_code == 200
    data = response.get_json()
    # Should handle the None URL and likely raise an error
    assert "log" in data


def test_convert_endpoint_file_not_found(client):
    """Test that the /convert endpoint handles FileNotFoundError correctly."""
    with patch("spoteezer.flask_app.get_item", side_effect=FileNotFoundError):
        response = client.post(
            "/convert",
            json={"initURL": "https://open.spotify.com/track/invalid"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["log"] == "Could not find track..."
        assert data["result"] == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
