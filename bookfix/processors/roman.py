"""
Roman numeral conversion utility for Bookfix.

Provides roman_to_arabic conversion for caps review editor.
"""

import re
from typing import Union


def roman_to_arabic(roman: str) -> Union[int, None]:
    """
    Converts a single Roman numeral string to its Arabic integer equivalent.

    Args:
        roman: Roman numeral string to convert

    Returns:
        Integer equivalent or None if not a valid Roman numeral or is "I"
    """
    roman = roman.upper()
    # skip lone "I"
    if roman == "I":
        return None

    # Strict validator for numerals 1–3999
    validator = r"^M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})$"
    if not re.fullmatch(validator, roman):
        return None

    # Map and compute using subtractive notation
    roman_map = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for ch in reversed(roman):
        val = roman_map[ch]
        total += val if val >= prev else -val
        prev = val

    return total
