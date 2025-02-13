import re
from typing import Any

def _pattern_keys(
    keys: list[str], 
    regex: bool = True,
    flags: re.RegexFlag = re.IGNORECASE,
    ) -> re.Pattern:
    """
    Create regex pattern for matching given keys.
    """
    if regex:
        # Regex pattern that matches any of the keys in the list
        pattern = rf"({'|'.join(keys)})"
    else:
        # \b is a word boundary, which matches the position where a word starts or ends
        pattern = rf"\b({'|'.join(keys)})\b"
    return re.compile(pattern, flags = flags)



def _pattern_start_keys(
    keys: list[str], 
    regex: bool = True,
    flags: re.RegexFlag = re.DOTALL | re.IGNORECASE
    ) -> Any:
    """
    Creates a regex pattern that matches the start of a string with any of the keys in the list.
    """
    if regex:
        # Regex pattern that matches any of the keys in the list
        pattern = rf"({'|'.join(keys)}).*?"
    else:
        # \b is a word boundary, which matches the position where a word starts or ends
        pattern = rf"\b({'|'.join(keys)})\b.*?"
    return re.compile(pattern, flags = flags)


def _get_first_key_match(
    text: str,
    keys: list[str], 
    regex: bool = True,
    **kwargs,
    ) -> str | Any | None:
    """
    Return the first key match (ignore case and include newline) in the text. If no match is found, return None.
    """
    pattern = _pattern_start_keys(keys, regex, **kwargs) 
    match = pattern.search(text)
    return match.group(1) if match else None



def _get_all_key_matches(
    text: str,
    keys: list[str], 
    regex: bool = True,
    **kwargs,
    ) -> list[Any]:
    """
    Return all key matches (ignore case and include newline) in the text. If no match is found, return an empty list.
    """
    pattern = _pattern_start_keys(keys, regex, **kwargs) 
    matches = pattern.findall(text)
    return matches