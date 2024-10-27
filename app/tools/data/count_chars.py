def count_chars(text, chars_lexical, feature_name):
    """
    Count occurrences of specific characters in a text, using a dictionary of chars with lexical names.

    :param text: The text to search within.
    :param chars_lexical: A dictionary of characters and their lexical names for which to count occurrences.
    :param feature_name: The name of the feature section (url, domain, path, query).
    :return: A dictionary with counts of specified characters in the text, using lexical names.
    """
    return {f"qty_{chars_lexical[char]}_{feature_name}": text.count(char) for char in chars_lexical}
