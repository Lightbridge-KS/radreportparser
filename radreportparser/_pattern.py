import re
from typing import Any, Literal, Optional, Union


def _try_import_re2() -> Optional[Any]:
    """
    Try to import re2 module and return it if successful.
    """
    try:
        import re2
        return re2
    except ImportError:
        return None


def _pattern_keys(
    keys: list[str], 
    word_boundary: bool = True,
    flags: Union[re.RegexFlag, int] = re.IGNORECASE,
    backend: Literal["re", "re2"] = "re"
    ) -> Any:
    """
    Create regex pattern for matching given keys.
    
    Parameters
    ----------
    keys : list[str]
        List of keys to match.
    word_boundary : bool, default=True
        Whether to use word boundaries in the pattern.
    flags : Union[re.RegexFlag, int], default=re.IGNORECASE
        Flags to use when compiling the pattern.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
    backend : {"re", "re2"}, default="re"
        Regex backend to use:
        - "re": Standard Python regex engine
        - "re2": Google's RE2 engine (must be installed)
        
    Returns
    -------
    Any
        Compiled regex pattern.
        
    Raises
    ------
    ValueError
        If keys is empty or if backend is "re2" but re2 is not installed.
    """
    if len(keys) == 0:
        raise ValueError("keys must have at least one element")
    
    # Create pattern string
    if word_boundary:
        # \b is a word boundary, which matches the position where a word starts or ends
        pattern = rf"\b({'|'.join(keys)})\b"
    else:
        # Regex pattern that matches any of the keys in the list
        pattern = rf"({'|'.join(keys)})"
    
    # Determine which regex backend to use
    if backend == "re":
        return re.compile(pattern, flags=flags)
    elif backend == "re2":
        regex_module = _try_import_re2()
        if regex_module is None:
            raise ValueError(
                "The 're2' backend was requested but the package is not installed. "
                "Please install it with 'pip install re2' or use the default 're' backend."
            )
        
        # Convert re flags to re2 options
        options = regex_module.Options()
        
        # Handle case sensitivity (most common flag)
        if flags & re.IGNORECASE:
            options.case_sensitive = False
            
        # Handle multiline flag
        if flags & re.MULTILINE:
            options.never_nl = False
            options.dot_nl = True
            
        # Handle dotall flag (. matches newlines)
        if flags & re.DOTALL:
            options.dot_nl = True
            
        # Note: re2 doesn't support all re flags, so some might be silently ignored
            
        return regex_module.compile(pattern, options=options)
    else:
        raise ValueError(f"Invalid backend: {backend}. Must be one of: 're', 're2'")
    

def _ensure_string(text: Any) -> str:
    """Convert input to string, handling various types safely.
    
    Parameters
    ----------
    text : Any
        The input to convert to string

    Returns
    -------
    str
        String representation of the input

    Raises
    ------
    TypeError
        If the input cannot be converted to string
    """
    if isinstance(text, str):
        return text
    elif isinstance(text, (int, float, bool)):
        return str(text)
    elif text is None:
        return ""
    elif hasattr(text, '__str__'):
        return str(text)
    else:
        raise TypeError(f"Cannot convert {type(text).__name__} to string")