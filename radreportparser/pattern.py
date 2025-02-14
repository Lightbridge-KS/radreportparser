import re
from typing import Any

def _pattern_keys(
    keys: list[str], 
    word_boundary: bool = True,
    flags: re.RegexFlag = re.IGNORECASE
    ) -> Any:
    """
    Create regex pattern for matching given keys.
    """
    if len(keys) == 0:
        raise ValueError("keys must have at least one element")
    
    if word_boundary:
        # \b is a word boundary, which matches the position where a word starts or ends
        pattern = rf"\b({'|'.join(keys)})\b"
    else:
        # Regex pattern that matches any of the keys in the list
        pattern = rf"({'|'.join(keys)})"
    return re.compile(pattern, flags = flags)



def _pattern_start_keys(
    keys: list[str], 
    word_boundary: bool = True,
    flags: re.RegexFlag = re.DOTALL | re.IGNORECASE
    ) -> Any:
    """
    Creates a regex pattern that matches the start of a string with any of the keys in the list.
    """
    if word_boundary:
        # \b is a word boundary, which matches the position where a word starts or ends
        pattern = rf"\b({'|'.join(keys)})\b.*?"
    else:
        # Regex pattern that matches any of the keys in the list
        pattern = rf"({'|'.join(keys)}).*?"
    return re.compile(pattern, flags = flags)


def _get_first_key_match(
    text: str,
    keys: list[str], 
    word_boundary: bool = True,
    **kwargs,
    ) -> str | Any | None:
    """
    Return the first key match (ignore case and include newline) in the text. If no match is found, return None.
    """
    pattern = _pattern_start_keys(keys, word_boundary, **kwargs) 
    match = pattern.search(text)
    return match.group(1) if match else None



def _get_all_key_matches(
    text: str,
    keys: list[str], 
    word_boundary: bool = True,
    **kwargs,
    ) -> list[Any]:
    """
    Return all key matches (ignore case and include newline) in the text. If no match is found, return an empty list.
    """
    pattern = _pattern_start_keys(keys, word_boundary, **kwargs) 
    matches = pattern.findall(text)
    return matches