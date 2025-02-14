import re
from typing import Literal
from .pattern import _pattern_keys


def extract_section(text, 
                    start_keys: list[str] | None,
                    end_keys: list[str] | None,
                    include_start_keys: bool = False,
                    word_boundary: bool = True,
                    flags: re.RegexFlag = re.IGNORECASE,
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
        Default is True.
    flags : re.RegexFlag, optional
        Regex flags to use in pattern matching.
        Default is `re.IGNORECASE`.

    Returns
    -------
    str or None
        The extracted section of text if found, `""` if no start key is found.

    Examples
    --------
    >>> text = "FINDINGS: Normal chest. IMPRESSION: No acute disease."
    >>> extract_section(text, ["FINDINGS:"], ["IMPRESSION:"])
    'Normal chest.'
    
    >>> # Multiple possible start keys
    >>> text = "TECHNIQUE: MRI scan. FINDINGS: Normal."
    >>> extract_section(text, ["FINDINGS:", "TECHNIQUE:"], None)
    'MRI scan.'
    
    >>> # Including start keys
    >>> extract_section(text, ["FINDINGS:"], None, include_start_keys=True)
    'FINDINGS: Normal.'
    
    >>> # No matches
    >>> extract_section(text, ["NOT_FOUND:"], None)
    """

    def find_start_position(text: str, keys: list[str] | None) -> tuple[int, int]:
        """Helper function to find start position of the section"""
        if keys is None:
            return 0, 0
        start_match = _pattern_keys(keys, word_boundary, flags).search(text)
        if not start_match:
            return -1, -1  # Indicate no match found
        return start_match.start(), start_match.end()
    
    def find_end_position(text: str, keys: list[str] | None, start_pos: int) -> int:
        """Helper function to find end position of the section"""
        if keys is None:
            return len(text)
        end_match = _pattern_keys(keys, word_boundary, flags).search(text[start_pos:])
        return len(text) if not end_match else start_pos + end_match.start()

    # Find start position
    start_idx_start, start_idx_end = find_start_position(text, start_keys)
    if start_idx_start == -1:  # No start match found
        return ""
    
    # Find end position
    end_idx = find_end_position(text, end_keys, start_idx_start)
    
    # Extract the section
    section_start = start_idx_start if include_start_keys else start_idx_end
    return text[section_start:end_idx].strip()