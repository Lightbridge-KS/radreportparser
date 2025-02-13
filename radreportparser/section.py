import re
from .pattern import _pattern_keys


def extract_section(
    text: str,
    start_keys: list[str],
    end_keys: list[str] | None,
    include_start_keys: bool = False,
    regex: bool = True,
    flags: re.RegexFlag = re.IGNORECASE,
):
    """Extract a section of text between specified start and end keys.

    This function searches for a section of text that begins with any of the start keys
    and ends with any of the end keys. If no end key is found, it extracts until the end
    of the text.

    Parameters
    ----------
    text : str
        The input text to search through.
    start_keys : list[str]
        List of possible section start markers.
    end_keys : list[str], None
        List of possible section end markers. If None, the section will be extracted
        until the end of the text.
    include_start_keys : bool, optional
        Whether to include the start key in the extracted section.
        Default is True.
    regex : bool, optional
        Whether to treat keys as regex patterns.
        Default is False.
    flags : re.RegexFlag, optional
        Regex flags to use in pattern matching.
        Default is re.IGNORECASE.

    Returns
    -------
    str or None
        The extracted section of text if found, None if no start key is found.

    Examples
    --------
    >>> text = "FINDINGS: Normal chest. IMPRESSION: No acute disease."
    >>> _extract_section(text, ["FINDINGS:"], ["IMPRESSION:"])
    'FINDINGS: Normal chest.'
    """
    # First find the starting point
    start_match = _pattern_keys(start_keys, regex, flags).search(text)

    if not start_match:
        return ""

    if end_keys is None:
        # If there are no end keys, extract the section from the start key to the end of the text
        end_idx = len(text)
    else:
        # Find the ending point
        end_match = _pattern_keys(end_keys, regex, flags).search(
            text[start_match.start() :]
        )
        if not end_match:
            end_idx = len(text)
        else:
            # Find the index of the end key in the original text
            end_idx = start_match.start() + end_match.start()

    if include_start_keys:
        # Extract the section with start key
        section = text[start_match.start() : end_idx].strip()
    else:
        # Extract the section without start key
        section = text[start_match.end() : end_idx].strip()
    return section
