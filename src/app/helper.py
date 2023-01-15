# List of special characters to remove from the strings, or to replace with a space.
SPE_CHARS = [(['&', '"', '#', '%', "'", '*', '+', ',', '.', ':', ';', '<', '=',
               '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '(', ')'], ''),
               (['  '], ' ')]


def get_first_value_with_substr(dictionary, key, substring):
    """Gets the first value of the given dictionary corresponding to the
    given key, and contains the given substring.

    Returns:
        str: The value corresponding to the given key and containing the
        given substring.
    """

    # If the given dictionary is indeed a dictionary
    if isinstance(dictionary, dict):
        # Check if the current level contains the key
        if key in dictionary and substring in dictionary[key]:
            return dictionary[key]
        # Otherwise, recursively search the nested dictionaries
        for value in dictionary.values():
            result = get_first_value_with_substr(value, key, substring)
            if result is not None:
                return result

    # If the given dictionary is actually a list
    elif isinstance(dictionary, list):
        # Recursively search the list elements
        for item in dictionary:
            result = get_first_value_with_substr(item, key, substring)
            if result is not None:
                return result
    return None


def preprocess_string(string: str):
    """Preprocesses the given string by:
    - Removing special characters,
    - Replacing some special characters with a space,
    - Converting to lowercase.

    Returns:
        str: The preprocessed string.
    """

    for char in SPE_CHARS[0][0]:
        if char in string:
            string = string.replace(char, SPE_CHARS[0][1])

    for char in SPE_CHARS[1][0]:
        if char in string:
            string = string.replace(char, SPE_CHARS[1][1])

    return string.lower()


def extract_web_info(item):
    """Extracts useful information for the web interfaces.

    Args:
        item (Item): The item from which to extract the information.

    Returns:
        dict: The extracted useful information.
    """

    return {'url': item.url,
            'type': item.type,
            'id': item.id,
            'platform': item.PLATFORM}
