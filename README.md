# Spoteezer
I am currently trying Deezer but have friends and family on Spotify.\
This repo will regroup some Deezer-to-Spotify utilities (and vice-versa).

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

Then create a file called `spotify_credentials.txt` at the root, and complete it as follows with your [Spotify developper app](https://developer.spotify.com/dashboard/applications) credentials:
```
[SPOTIFY_CLIENT_ID]
[SPOTIFY_CLIENT_SECRET]
```

## Usage

### Convert a Deezer link to a Spotify link

⚠️ Works for single tracks, albums, and artists

Make sure you are in the `src` folder and run:

`python convert_link.py [deezer_link]`

On Mac, you can use the following shortcut to quickly convert links:
https://www.icloud.com/shortcuts/562d373485a84d6a9ac64e3df6bd19d1
