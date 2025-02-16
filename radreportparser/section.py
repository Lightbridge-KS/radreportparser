import re
from typing import (
    Literal,
    List,
    Tuple,
)
from ._pattern import _pattern_keys

## Start Position


def _find_start_position(
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


def _find_start_position_all(
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


class SectionExtractor:
    """Extract sections from text based on start and end keys.

    This class provides functionality to extract sections of text that begin with
    any of the start keys and end just before any of the end keys (i.e., not include the end keys).

    - If no start key is found, return `""`.
    - If start key is `None`, the section will start from the beginning of the text until the end key (exclusive).
    - If no end key is found or end key is `None`, it extracts until the end of the text.

    Parameters
    ----------
    start_keys : list[str] | None
        List of possible section start markers. If None, the section will be
        extracted from the beginning of the text.
    end_keys : list[str] | None
        List of possible section end markers. The `end_key` will not be included in the extracted section. If None, the section will be
        extracted until the end of the text.
    include_start_keys : bool, optional
        Whether to include the start key in the extracted section.
        Default is True.
    word_boundary : bool, optional
        Whether to wrap word boundary `\b` around the keys.
        Default is True.
    flags : re.RegexFlag, optional
        Regex flags to use in pattern matching.
        Default is `re.IGNORECASE`.
    match_strategy : {"greedy", "sequential"}, optional
        Strategy for matching end keys:
        - "greedy": Use first matching end key (faster)
        - "sequential": Try end keys in order (more precise)
        Default is "greedy".

    Examples
    --------
    ```{python}
    from radreportparser import SectionExtractor
    # Create an extractor for finding text between headers
    extractor = SectionExtractor(
        start_keys=["FINDINGS:"],
        end_keys=["IMPRESSION:", "CONCLUSION:"]
    )
    print(extractor)
    ```
    """

    def __init__(
        self,
        start_keys: list[str] | None,
        end_keys: list[str] | None,
        include_start_keys: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ):
        self.start_keys = start_keys
        self.end_keys = end_keys
        self.include_start_keys = include_start_keys
        self.word_boundary = word_boundary
        self.flags = flags

        # Validate match strategy
        match_strategy_options = frozenset({"greedy", "sequential"})
        if match_strategy not in match_strategy_options:
            raise ValueError(
                f"Invalid value: {match_strategy}. "
                f"Must be one of: {', '.join(match_strategy_options)}"
            )
        self.match_strategy = match_strategy

    def __repr__(self) -> str:
        """Return a detailed string representation of the SectionExtractor."""
        # Format start_keys and end_keys lists
        start_keys_str = (
            f"[{', '.join(repr(k) for k in self.start_keys)}]"
            if self.start_keys
            else "None"
        )
        end_keys_str = (
            f"[{', '.join(repr(k) for k in self.end_keys)}]"
            if self.end_keys
            else "None"
        )

        # Format flags
        flags_name = self.flags.name if hasattr(self.flags, "name") else str(self.flags)

        return (
            f"{self.__class__.__name__}("
            f"start_keys={start_keys_str}, "
            f"end_keys={end_keys_str}, "
            f"include_start_keys={self.include_start_keys=}, "
            f"word_boundary={self.word_boundary}, "
            f"flags=re.{flags_name}, "
            f"match_strategy='{self.match_strategy}')"
        )

    def extract(
        self,
        text: str,
        verbose: bool = True,
    ) -> str:
        """Extract a section from the text using configured patterns.

        Extract a section from text if any of `start_keys` matches.
        If multiple `start_keys` matches are found in `text`, return section from the first match.

        Parameters
        ----------
        text : str
            The input text to extract section from.
        verbose : bool
            If `true` and there are more than one position of `text` that matches the `start_keys`, print message to standard output. 

        Returns
        -------
        str
            The extracted section text. Returns empty string if section not found.

        Examples
        --------
        ```{python}
        # Create an extractor for finding text
        from radreportparser import SectionExtractor
        extractor = SectionExtractor(
            start_keys=["FINDINGS:"],
            end_keys=["IMPRESSION:"]
        )
        # Extract section from text
        text = "FINDINGS: Normal. IMPRESSION: Clear."
        section = extractor.extract(text)
        print(section)
        ```
        """
        # Find start position
        start_idx_start, start_idx_end = _find_start_position(
            text,
            self.start_keys,
            word_boundary=self.word_boundary,
            flags=self.flags,
            verbose=verbose,
        )
        if start_idx_start == -1:  # No start match found
            return ""

        # Find end position based on strategy
        if self.match_strategy == "greedy":
            end_idx = _find_end_position_greedy(
                text,
                self.end_keys,
                start_idx_start,
                word_boundary=self.word_boundary,
                flags=self.flags,
            )
        else:
            end_idx = _find_end_position_sequential(
                text,
                self.end_keys,
                start_idx_start,
                word_boundary=self.word_boundary,
                flags=self.flags,
            )

        # Extract the section
        section_start = start_idx_start if self.include_start_keys else start_idx_end
        return text[section_start:end_idx].strip()

    def extract_all(self, text: str) -> List[str]:
        """Extract all sections from the text that match the configured patterns.

        Extract one or more section(s) from text if any of `start_keys` matches.


        Parameters
        ----------
        text : str
            The input text to extract sections from

        Returns
        -------
        List[str]
            List of extracted section texts. Returns empty list if no sections found.

        Examples
        --------
        ```{python}
        # Create an extractor for finding text
        from radreportparser import SectionExtractor
        extractor = SectionExtractor(
            start_keys=["FINDING:"],
            end_keys=["IMPRESSION:"]
        )
        text = '''
        FINDING: First observation
        IMPRESSION: OK
        FINDING: Second observation
        IMPRESSION: Also OK
        '''
        sections = extractor.extract_all(text)
        print(sections)
        ```
        """
        # Find all start positions
        start_positions = _find_start_position_all(
            text, self.start_keys, self.word_boundary, self.flags
        )

        if not start_positions:
            return []

        sections = []

        # Process each start position
        for start_idx_start, start_idx_end in start_positions:
            # Find end position based on strategy
            if self.match_strategy == "greedy":
                end_idx = _find_end_position_greedy(
                    text, self.end_keys, start_idx_start, self.word_boundary, self.flags
                )
            else:
                end_idx = _find_end_position_sequential(
                    text, self.end_keys, start_idx_start, self.word_boundary, self.flags
                )

            # Extract the section
            section_start = (
                start_idx_start if self.include_start_keys else start_idx_end
            )
            section = text[section_start:end_idx].strip()

            if section:  # Only add non-empty sections
                sections.append(section)

        return sections
