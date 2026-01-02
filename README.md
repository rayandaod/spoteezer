# Spoteezer

<img src="frontend/assets/spoteezer.png" width="100" height="100">

Convert Deezer links to Spotify links (and vice-versa) for tracks, albums, and artists.

[Online demo](https://rayan.daodnathoo.com/spoteezer) | [Demo GIF](assets/convert_link_web.gif)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rayandaod/spoteezer
   cd spoteezer
   ```

2. Install [`uv`](https://github.com/astral-sh/uv) (if needed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Set environment variables (add to your shell profile):
   ```bash
   export SPOTIFY_CLIENT_ID='[your_spotify_client_id]'
   export SPOTIFY_CLIENT_SECRET='[your_spotify_client_secret]'
   ```
   Get credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).

## Usage

Start the server:
```bash
just run
```

Then open `frontend/index.html` in your browser. The server runs on `127.0.0.1:8080`.

**macOS Shortcut**: [Install shortcut](https://www.icloud.com/shortcuts/562d373485a84d6a9ac64e3df6bd19d1) for quick clipboard conversion. [Demo GIF](assets/convert_link_shortcut.gif)

## Development

```bash
just test    # Run tests
just lint    # Lint code
just type    # Type check
```
