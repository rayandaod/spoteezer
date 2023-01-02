# List of special characters to remove from the strings, or to replace with a space.
SPE_CHARS = (['&', '"', '#', '%', "'", '*', '+', ',', '.', '/', ':', ';', '<', '=',
             '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '(', ')'], '')
SPE_CHARS_WITH_REPLACE = (['  '], ' ')


# For each item type, an ordereds list of search queries is defined.
# The order is important, as the first query is the most specific
# and the last query is the most general and the most required
# at the same time.
SEARCH_TRIAL_DICT = {'track': [['track', 'artist', 'album'],
                               ['track', 'artist'],
                               ['track']],
                     'album': [['album', 'artist'],
                               ['album']],
                     'artist': [['artist']]
                     }


def get_spotify_item_info(spotify_results, item_type):
    """
    Get the specified information from the Spotify results.
    The info_list is a list of strings that can be either 'track', 'artist' or 'album'.
    The item_type is a string that can be either 'track', 'album' or 'artist'.
    """

    # Get the first item from the results
    spotify_item = spotify_results[f'{item_type}s']['items'][0]

    # Initialize the info dictionary
    spotify_item_info = {}

    # Get the artist or artists
    def _get_artists(spotify_item_info, spotify_item):
        if len(spotify_item['artists']) > 1:
            spotify_item_info['artists'] = ', '.join([spotify_item['artists'][i]['name'] for i in range(len(spotify_item['artists']))])
        else:
            spotify_item_info['artist'] = spotify_item['artists'][0]['name']
        return spotify_item_info

    # For each info type, get the corresponding info from the item
    if item_type == 'track':
        spotify_item_info['track'] = spotify_item['name']
        spotify_item_info = _get_artists(spotify_item_info, spotify_item)
        spotify_item_info['album'] = spotify_item['album']['name']
    elif item_type == 'album':
        spotify_item_info['album'] = spotify_item['name']
        spotify_item_info = _get_artists(spotify_item_info, spotify_item)
    elif item_type == 'artist':
        spotify_item_info['artist'] = spotify_item['name']

    return spotify_item_info


if __name__ == '__main__':
    pass