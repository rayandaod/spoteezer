# Spoteezer

<img src="resources/spoteezer.png" width="100" height="100">

I am currently trying Deezer but have friends and family on Spotify.\
This repo will regroup some Deezer-to-Spotify utilities (and vice-versa).

[Online demo](https://rayan.daodnathoo.com/spoteezer)

![alt text](resources/convert_link_web.gif)

## Installation

First, you should clone the repository and navigate to it:
```
git clone https://github.com/rayandaod/spoteezer
cd spoteezer
```

Then, you need to install some useful libraries.\
Best practice is to create a separate environment, so let's do that with conda.
```
conda env create -f environment.yml
conda activate spoteezer
```

Then add the following environment variables to your `.zshrc` / `.bashrc` / ... profile:

```
export SPOTIFY_CLIENT_ID='[your_spotify_client_id]'
export SPOTIFY_CLIENT_SECRET='[your_spotify_client_secret]'
```

You can get these information by creating a [Spotify developper app](https://developer.spotify.com/dashboard/applications).

## Usage

### Convert a Deezer link to a Spotify link

⚠️ Works for single tracks, albums, and artists


#### Command line

Make sure you are in the conda environment and that you are located in the `src` folder, and run:\
`python convert_link.py [deezer_link]`

#### Flask app + HTML webpage

([Online demo](https://rayan.daodnathoo.com/spoteezer))

To run everything locally, you'll need to modify `webpage.html` to communicate with your local Flask server (`127.0.0.1:5000/convert` root).

Then:

- Run `python flask_app.py`
- Open `webpage.html`

#### MacOS shortcut (Apple Shortcuts)

![alt text](resources/convert_link_shortcut.gif)

To do so, install the following shortcut and modify it to match your paths:
https://www.icloud.com/shortcuts/562d373485a84d6a9ac64e3df6bd19d1

You can also pin it to the menu bar as I did for a quicker access.

- Copy the Deezer link to your clipboard.
- Run the shortcut.
- The resulting Spotify link shortly appears in your clipboard.
- Paste it wherever you want!
