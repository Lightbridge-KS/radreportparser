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
