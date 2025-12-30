"""Pytest configuration and fixtures for spoteezer tests."""

import os

# Set environment variables before any imports to avoid credential errors
os.environ.setdefault("SPOTIFY_CLIENT_ID", "test_client_id")
os.environ.setdefault("SPOTIFY_CLIENT_SECRET", "test_client_secret")

