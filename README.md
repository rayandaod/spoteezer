# spoteezer
I am currently trying Deezer but have friends and family on Spotify.\
This repo will regroup some Deezer-to-Spotify utilities (and vice-versa).

## Installation

First clone the repository:\
`git clone https://github.com/rayandaod/spoteezer`

You need to pip install some useful libraries.\
It is recommended to use a conda environment to keep your python installation clean.\
`pip install -r requirements.txt`

Then create a file called `spotify_credentials.txt` at the root of this repo.\
Put your application client id in the first line of the txt file.
And the application client secret in the second line of the txt file.

## Deezer link to Spotify link (only track links for now)
Very useful to send Deezer music to Spotify users.

Usage: `python d2s.py [deezer_link]`

On Mac, you can use the following shortcut to quickly convert links:
https://www.icloud.com/shortcuts/562d373485a84d6a9ac64e3df6bd19d1
