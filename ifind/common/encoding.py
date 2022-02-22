import string


def encode_symbols(instring):
    """
    Encodes symbols for HTTP GET.

    Args:
        string (str): String to be included in a GET request.

    Returns:
        str: String with some characters replaced with URL encodings.

    Usage:
        Private method.

    """
    encoded_string = string.replace(instring, "'", '%27')
    encoded_string = string.replace(encoded_string, '"', '%27')
    encoded_string = string.replace(encoded_string, '+', '%2b')
    encoded_string = string.replace(encoded_string, ' ', '%20')
    encoded_string = string.replace(encoded_string, ':', '%3a')

    return encoded_string