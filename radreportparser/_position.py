import re
from typing import (
    List,
    Tuple,
    Literal,
    Union,
)
from ._pattern import (
    _pattern_keys,
    _ensure_string
    )

## Start Position

def _find_start_position_greedy(
    text: str,
    keys: list[str] | None,
    word_boundary: bool = False,
    flags: Union[re.RegexFlag, int] = re.IGNORECASE,
    verbose: bool = True,
    backend: Literal["re", "re2"] = "re",
) -> tuple[int, int]:
    """Helper function to find start position of the section
    
    Parameters
    ----------
    text : str
        The input text to search through
    keys : list[str] | None
        List of possible section start markers
    word_boundary : bool, optional
        Whether to use word boundaries in pattern matching
    flags : Union[re.RegexFlag, int], optional
        Regex flags to use in pattern matching.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
    verbose : bool, optional
        If True, prints warnings when multiple start matches are found
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)
    
    Returns
    -------
    tuple[int, int]
        A tuple containing (start, end) positions.
        Returns (0, 0) if keys is None.
        Returns (-1, -1) if no matches found.
    """
    # Convert text to string
    text = _ensure_string(text)
    
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

    start_match = _pattern_keys(keys, word_boundary, flags, backend=backend).search(text)
    if not start_match:
        return -1, -1  # Indicate no match found
    return start_match.start(), start_match.end()


def _find_start_position_greedy_all(
    text: str,
    keys: list[str] | None,
    word_boundary: bool = False,
    flags: Union[re.RegexFlag, int] = re.IGNORECASE,
    backend: Literal["re", "re2"] = "re",
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
    flags : Union[re.RegexFlag, int], optional
        Regex flags to use in pattern matching.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)

    Returns
    -------
    List[Tuple[int, int]]
        List of tuples containing (start, end) positions of all matches.
        Returns [(0, 0)] if keys is None.
        Returns [] if no matches found.
    """
    # Convert text to string
    text = _ensure_string(text)
    
    if keys is None:
        return [(0, 0)]

    pattern = _pattern_keys(keys, word_boundary, flags, backend=backend)
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    return [(m.start(), m.end()) for m in matches]


def _find_start_position_sequential(
    text: str,
    keys: list[str] | None,
    word_boundary: bool = False,
    flags: Union[re.RegexFlag, int] = re.IGNORECASE,
    verbose: bool = True,
    backend: Literal["re", "re2"] = "re",
) -> tuple[int, int]:
    """Find the start position of a section using sequential matching.

    Tries each start key in order and returns the position of the first successful match.
    More precise when the order of keys matters.

    Parameters
    ----------
    text : str
        The input text to search through
    keys : list[str] | None
        List of possible start markers, tried in order
    word_boundary : bool, optional
        Whether to use word boundaries in pattern matching
    flags : Union[re.RegexFlag, int], optional
        Regex flags to use in pattern matching.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
    verbose : bool, optional
        If True, prints warning when multiple matches are found
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)

    Returns
    -------
    tuple[int, int]
        A tuple containing (start, end) positions.
        Returns (0, 0) if keys is None.
        Returns (-1, -1) if no matches found.
    """
    # Convert text to string
    text = _ensure_string(text)
    
    if keys is None:
        return 0, 0

    # Try each key in sequence
    for key in keys:
        # Create pattern for single key
        pattern = _pattern_keys([key], word_boundary, flags, backend=backend)
        match = pattern.search(text)

        if match:
            # Warn if pattern appears more than once
            if verbose:
                all_matches = list(pattern.finditer(text))
                if len(all_matches) >= 2:
                    print(
                        f"Start pattern {key} appears {len(all_matches)} times in text, "
                        "only the first one will be matched."
                    )
            return match.start(), match.end()

    # If no matches found, return indicator
    return -1, -1


def _find_start_position_sequential_all(
    text: str,
    keys: list[str] | None,
    word_boundary: bool = False,
    flags: Union[re.RegexFlag, int] = re.IGNORECASE,
    backend: Literal["re", "re2"] = "re",
) -> List[Tuple[int, int]]:
    """Find all start positions of sections using sequential matching.

    Tries each start key in order and collects all successful matches.
    This follows the sequential strategy where the order of keys matters.

    Parameters
    ----------
    text : str
        The input text to search through
    keys : list[str] | None
        List of possible section start markers to try in order
    word_boundary : bool, optional
        Whether to use word boundaries in pattern matching
    flags : Union[re.RegexFlag, int], optional
        Regex flags to use in pattern matching.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)

    Returns
    -------
    List[Tuple[int, int]]
        List of tuples containing (start, end) positions of all matches.
        Returns [(0, 0)] if keys is None.
        Returns [] if no matches found.
    """
    # Convert text to string
    text = _ensure_string(text)
    
    if keys is None:
        return [(0, 0)]

    all_positions = []
    
    # Try each key in sequence
    for key in keys:
        # Create pattern for single key
        pattern = _pattern_keys([key], word_boundary, flags, backend=backend)
        
        # Find all matches for this key
        matches = list(pattern.finditer(text))
        if matches:
            # Add all positions for this key
            all_positions.extend([(m.start(), m.end()) for m in matches])
    
    # Sort positions by start index to maintain document order
    return sorted(all_positions) if all_positions else []


## End Position


def _find_end_position_greedy(
    text: str,
    keys: list[str] | None,
    start_pos: int,
    word_boundary: bool = False,
    flags: Union[re.RegexFlag, int] = re.IGNORECASE,
    backend: Literal["re", "re2"] = "re",
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
    flags : Union[re.RegexFlag, int], optional
        Regex flags to use in pattern matching.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)

    Returns
    -------
    int
        The ending position in the text
    """
    # Convert text to string
    text = _ensure_string(text)
    
    if keys is None:
        return len(text)
    end_match = _pattern_keys(keys, word_boundary, flags, backend=backend).search(text[start_pos:])
    return len(text) if not end_match else start_pos + end_match.start()


def _find_end_position_sequential(
    text: str,
    keys: list[str] | None,
    start_pos: int,
    word_boundary: bool = False,
    flags: Union[re.RegexFlag, int] = re.IGNORECASE,
    backend: Literal["re", "re2"] = "re",
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
    flags : Union[re.RegexFlag, int], optional
        Regex flags to use in pattern matching.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)

    Returns
    -------
    int
        The ending position in the text
    """
    # Convert text to string
    text = _ensure_string(text)
    
    if keys is None:
        return len(text)

    search_text = text[start_pos:]

    # Try each key in sequence
    for key in keys:
        # Create pattern for single key
        pattern = _pattern_keys([key], word_boundary, flags, backend=backend)
        match = pattern.search(search_text)

        if match:
            # Return position relative to original text
            return start_pos + match.start()

    # If no matches found, return end of text
    return len(text)