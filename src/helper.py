import requests


# List of special characters to remove from the strings, or to replace with a space.
SPE_CHARS = (['&', '"', '#', '%', "'", '*', '+', ',', '.', '/', ':', ';', '<', '=',
             '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '(', ')'], '')
SPE_CHARS_WITH_REPLACE = (['  '], ' ')


# For each item type, a list of search queries is defined.
# The order is important, as the first query is the most specific.
SEARCH_TRIAL_DICT = {'track': [['track', 'artist', 'album'],
                               ['track', 'artist'],
                               ['track']],
                     'album': [['album', 'artist'],
                               ['album']],
                     'artist': [['artist']]
                     }


def get_first_value_with_substr(dictionary, key, substring):
    """
    Get the first value of a dictionary that corresponds to the specified key,
    and contains a specified substring.
    The data is a dictionary.
    The key is the key of the dictionary.
    The substring is the substring to search for.
    """

    if isinstance(dictionary, dict):
        # Check if the current level contains the key
        if key in dictionary and substring in dictionary[key]:
            return dictionary[key]
        # Otherwise, recursively search the nested dictionaries
        for value in dictionary.values():
            result = get_first_value_with_substr(value, key, substring)
            if result is not None:
                return result
    elif isinstance(dictionary, list):
        # Recursively search the list elements
        for item in dictionary:
            result = get_first_value_with_substr(item, key, substring)
            if result is not None:
                return result
    return None


def get_final_url(url):
    """
    Get the final url of a link, i.e after redirections.
    """
    responses = requests.get(url)

    if len(responses.history) > 0:
        return responses.history[-1].url
    else:
        return responses.url


def preprocess_string(string):
    """
    Preprocess a string by:
    - removing special characters
    - replacing some special characters with a space
    - converting to lowercase
    """

    for char in SPE_CHARS[0]:
        if char in string:
            string = string.replace(char, SPE_CHARS[1])

    for char in SPE_CHARS_WITH_REPLACE[0]:
        if char in string:
            string = string.replace(char, SPE_CHARS_WITH_REPLACE[1])

    return string.lower()
