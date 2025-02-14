import re
import logging
from typing import Literal
from ._pattern import _pattern_keys

## Start Position

def _find_start_position(text: str, 
                        keys: list[str] | None,
                        word_boundary: bool = False,
                        flags: re.RegexFlag = re.IGNORECASE,
                        ) -> tuple[int, int]:
    """Helper function to find start position of the section"""
    if keys is None:
        return 0, 0
    # Warn if start pattern appears more than once
    for key in keys:
        x = re.findall(key, text, flags)
        count = len(x)
        if count >= 2:
            logging.warning("Start pattern `%s` appear %d times in text, only the first one will be matched.", key, count)
            
    start_match = _pattern_keys(keys, word_boundary, flags).search(text)
    if not start_match:
        return -1, -1  # Indicate no match found
    return start_match.start(), start_match.end()


## End Position


def _find_end_position_greedy(text: str, 
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


def _find_end_position_sequential(text: str, 
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



def extract_section(text: str,
                   start_keys: list[str] | None,
                   end_keys: list[str] | None,
                   include_start_keys: bool = False,
                   word_boundary: bool = False,
                   flags: re.RegexFlag = re.IGNORECASE,
                   match_strategy: Literal["greedy", "sequential"] = "greedy",
                   ) -> str | Literal[""]:
    """Extract a section of text between specified start and end keys.

    This function searches for a section of text that begins with any of the start keys
    and ends with any of the end keys. 
    
    - If no start key is found, return `""`.  
    - If start key is `None`, the section will start from the beginning of the text unitl the end key (if found).
    - If no end key is found or end key is `None`, it extracts until the end of the text.

    Parameters
    ----------
    text : str
        The input text to search through.
    start_keys : list[str], None
        List of possible section start markers. If None, the section will be extracted from the beginning of the text.
    end_keys : list[str], None
        List of possible section end markers. If None, the section will be extracted
        until the end of the text.
    include_start_keys : bool, optional
        Whether to include the start key in the extracted section.
        Default is True.
    word_boundary : bool, optional
        Whether to wrap word boundary `\b` around the `start_keys` and `end_keys`.
        Default is False.
    flags : re.RegexFlag, optional
        Regex flags to use in pattern matching.
        Default is `re.IGNORECASE`.
    match_strategy : MatchStrategy, optional
        Strategy for matching end keys:
        - "greedy": Use first matching end key (faster)
        - "sequential": Try end keys in order (more precise)
        Default is "greedy"

    
    Examples
    --------
    >>> text = "FINDINGS: Normal. TECHNIQUE: MRI. IMPRESSION: Clear."
    >>> # Using sequential matching
    >>> extract_section(text, ["FINDINGS:"], 
    ...                ["TECHNIQUE:", "IMPRESSION:"],
    ...                match_strategy="sequential")
    'Normal.'
    """
    # Find start position    
    start_idx_start, start_idx_end = _find_start_position(text, start_keys, word_boundary=word_boundary, flags=flags)
    if start_idx_start == -1:  # No start match found
        return ""
    
    # Find end position based on strategy
    match_strategy_options =  frozenset({"greedy", "sequential"})
    if match_strategy not in match_strategy_options:
        raise ValueError(f"Invalid value: {match_strategy}. Must be one of: {', '.join(match_strategy_options)}")
    
    if match_strategy == "greedy":
        end_idx = _find_end_position_greedy(text, end_keys, start_idx_start, word_boundary=word_boundary, flags=flags)
    else:
        end_idx = _find_end_position_sequential(text, end_keys, start_idx_start, word_boundary=word_boundary, flags=flags)
    
    # Extract the section
    section_start = start_idx_start if include_start_keys else start_idx_end
    return text[section_start:end_idx].strip()