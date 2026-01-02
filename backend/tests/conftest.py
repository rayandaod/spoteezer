"""Pytest configuration and fixtures for spoteezer tests."""

import os
import pytest

# Set environment variables before any imports to avoid credential errors
os.environ.setdefault("SPOTIFY_CLIENT_ID", "test_client_id")
os.environ.setdefault("SPOTIFY_CLIENT_SECRET", "test_client_secret")


def pytest_addoption(parser):
    """Add custom command-line options for pytest."""
    parser.addoption(
        "--url",
        action="store",
        default=None,
        help="URL to test (Spotify or Deezer link)",
    )


@pytest.fixture
def test_url(request):
    """Fixture to get the URL from command-line option."""
    return request.config.getoption("--url")
