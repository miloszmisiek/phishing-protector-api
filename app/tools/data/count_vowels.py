def count_vowels(text):
    """
    Count the number of vowels in a text.

    :param text: The text to search within.
    :return: The number of vowels in the text.
    """
    vowels = 'aeiou'
    return sum(1 for char in text if char.lower() in vowels)