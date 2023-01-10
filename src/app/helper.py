import requests


# List of special characters to remove from the strings, or to replace with a space.
SPE_CHARS = (['&', '"', '#', '%', "'", '*', '+', ',', '.', '/', ':', ';', '<', '=',
             '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '(', ')'], '')
SPE_CHARS_WITH_REPLACE = (['  '], ' ')


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


def extract_web_info(item=None, init=False, logger=None):
    web_info = {'result_link': '',
                'platform': '',
                'img_src': '',
                'info': {},
                'type': ''}
    if item:
        web_info = {'result_link': item.link,
                    'platform': item.platform,
                    'img_src': item.img_link,
                    'info': item.info_simple,
                    'type': item.type}

    return web_info
