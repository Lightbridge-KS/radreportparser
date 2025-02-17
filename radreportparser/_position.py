import re
from typing import (
    List,
    Tuple,
)
from ._pattern import _pattern_keys

## Start Position

def _find_start_position_greedy(
    text: str,
    keys: list[str] | None,
    word_boundary: bool = False,
    flags: re.RegexFlag = re.IGNORECASE,
    verbose: bool = True,
) -> tuple[int, int]:
    """Helper function to find start position of the section"""
    if keys is None:
        return 0, 0
    # Warn if start pattern appears more than once
    for key in keys:
        x = re.findall(key, text, flags)
        count = len(x)
        if verbose and count >= 2:
            print(
                f"Start pattern {key} appear {count} times in text, only the first one will be matched."
            )

    start_match = _pattern_keys(keys, word_boundary, flags).search(text)
    if not start_match:
        return -1, -1  # Indicate no match found
    return start_match.start(), start_match.end()


def _find_start_position_greedy_all(
    text: str,
    keys: list[str] | None,
    word_boundary: bool = False,
    flags: re.RegexFlag = re.IGNORECASE,
) -> List[Tuple[int, int]]:
    """Helper function to find all start positions of the sections.

    Parameters
    ----------
    text : str
        The input text to search through
    keys : list[str] | None
        List of possible section start markers
    word_boundary : bool, optional
        Whether to use word boundaries in pattern matching
    flags : re.RegexFlag, optional
        Regex flags to use in pattern matching

    Returns
    -------
    List[Tuple[int, int]]
        List of tuples containing (start, end) positions of all matches.
        Returns [(0, 0)] if keys is None.
        Returns [] if no matches found.
    """
    if keys is None:
        return [(0, 0)]

    pattern = _pattern_keys(keys, word_boundary, flags)
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    return [(m.start(), m.end()) for m in matches]


## End Position


def _find_end_position_greedy(
    text: str,
    keys: list[str] | None,
    start_pos: int,
    word_boundary: bool = False,
    flags: re.RegexFlag = re.IGNORECASE,
) -> int:
    """Find the end position of a section using greedy matching.

    Searches for any of the end keys and returns the position of the first match found.
    This is faster but less precise when order matters.

    Parameters
    ----------
    text : str
        The input text to search through
    keys : list[str] | None
        List of possible end markers
    start_pos : int
        Position in text to start searching from
    word_boundary : bool, optional
        Whether to use word boundaries in pattern matching
    flags : re.RegexFlag, optional
        Regex flags to use in pattern matching

    Returns
    -------
    int
        The ending position in the text
    """
    if keys is None:
        return len(text)
    end_match = _pattern_keys(keys, word_boundary, flags).search(text[start_pos:])
    return len(text) if not end_match else start_pos + end_match.start()


def _find_end_position_sequential(
    text: str,
    keys: list[str] | None,
    start_pos: int,
    word_boundary: bool = False,
    flags: re.RegexFlag = re.IGNORECASE,
) -> int:
    """Find the end position of a section using sequential matching.

    Tries each end key in order and returns the position of the first successful match.
    More precise when the order of keys matters.

    Parameters
    ----------
    text : str
        The input text to search through
    keys : list[str] | None
        List of possible end markers, tried in order
    start_pos : int
        Position in text to start searching from
    word_boundary : bool, optional
        Whether to use word boundaries in pattern matching
    flags : re.RegexFlag, optional
        Regex flags to use in pattern matching

    Returns
    -------
    int
        The ending position in the text
    """
    if keys is None:
        return len(text)

    search_text = text[start_pos:]

    # Try each key in sequence
    for key in keys:
        # Create pattern for single key
        pattern = _pattern_keys([key], word_boundary, flags)
        match = pattern.search(search_text)

        if match:
            # Return position relative to original text
            return start_pos + match.start()

    # If no matches found, return end of text
    return len(text)