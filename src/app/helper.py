import requests

from rules import SPE_CHARS, SPE_CHARS_WITH_REPLACE


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


def get_final_link(link, logger=None):
    """
    Get the final link of a link, i.e after redirections.
    """
    responses = requests.get(link)

    if len(responses.history) > 0:
        final_link = responses.history[-1].url
    else:
        final_link = responses.url

    if logger is not None:
        logger.info(f'Final link = {final_link}')
    
    return final_link


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
