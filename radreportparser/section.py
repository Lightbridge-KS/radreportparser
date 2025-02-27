import re
from typing import (
    Literal,
    List,
    Union,
)
from ._position import (
    _find_start_position_greedy,
    _find_start_position_sequential,
    _find_start_position_greedy_all,
    _find_end_position_greedy,
    _find_end_position_sequential,
    _find_start_position_sequential_all
)


class SectionExtractor:
    """Extract sections from text based on start and end keys.

    This class provides functionality to extract sections of text that begin with
    any of the start keys and end just before any of the end keys (i.e., not include the end keys).

    - If no start key is found, return `""`.
    - If start key is `None`, the section will start from the beginning of the text until the end key (exclusive).
    - If no end key is found or end key is `None`, it extracts until the end of the text.
    
    **`match_strategy`:** Strategy for matching both start and end keys:
    
    - "greedy" (default):
        - Scans text from left to right
        - Returns first match found for any pattern in keys
        - Order of patterns in keys list doesn't matter
        - Faster but less precise when order matters
    
    - "sequential":
        - Tries each pattern in keys list in order
        - Returns first successful match
        - Order of patterns in keys list matters
        - More precise but slightly slower

    Parameters
    ----------
    start_keys : list[str] | None
        List of possible section start markers as regular expression. If None, the section will be
        extracted from the beginning of the text.
    end_keys : list[str] | None
        List of possible section end markers as regular expression. The `end_key` will not be included in the extracted section. If None, the section will be
        extracted until the end of the text.
    include_start_keys : bool, optional
        Whether to include the start key in the extracted section.
        Default is True.
    word_boundary : bool, optional
        Whether to wrap word boundary `\b` around the keys.
        Default is True.
    flags : Union[re.RegexFlag, int], optional
        Regex flags to use in pattern matching.
        For 're' backend: These are directly passed to re.compile()
        For 're2' backend: These are converted to re2.Options properties
        Default is `re.IGNORECASE`.
    match_strategy : {"greedy", "sequential"}, optional
        Strategy for matching both start and end keys.
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)

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
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        backend: Literal["re", "re2"] = "re",
    ):
        self.start_keys = start_keys
        self.end_keys = end_keys
        self.include_start_keys = include_start_keys
        self.word_boundary = word_boundary
        self.flags = flags
        self.backend = backend

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
            f"include_start_keys={self.include_start_keys}, "
            f"word_boundary={self.word_boundary}, "
            f"flags=re.{flags_name}, "
            f"match_strategy='{self.match_strategy}', "
            f"backend='{self.backend}')"
        )

    def extract(
        self,
        text: str,
        verbose: bool = True,
    ) -> str:
        """Extract a section from the text using configured patterns.

        Extract a section from text if any of `start_keys` matches.
        If multiple `start_keys` matches are found in `text`, return section from the first match. 
        The matching strategy is controlled by `match_strategy` argument in the initialization of `SectionExtractor()`

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
        # Find start position based on strategy
        if self.match_strategy == "greedy":
            start_idx_start, start_idx_end = _find_start_position_greedy(
                text,
                self.start_keys,
                word_boundary=self.word_boundary,
                flags=self.flags,
                verbose=verbose,
                backend=self.backend,
            )
        else:
            start_idx_start, start_idx_end = _find_start_position_sequential(
                text,
                self.start_keys,
                word_boundary=self.word_boundary,
                flags=self.flags,
                verbose=verbose,
                backend=self.backend,
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
                backend=self.backend,
            )
        else:
            end_idx = _find_end_position_sequential(
                text,
                self.end_keys,
                start_idx_start,
                word_boundary=self.word_boundary,
                flags=self.flags,
                backend=self.backend,
            )

        # Extract the section
        section_start = start_idx_start if self.include_start_keys else start_idx_end
        return text[section_start:end_idx].strip()

    def extract_all(self, text: str) -> List[str]:
        """Extract all sections from the text that match the configured patterns.

        Extract one or more section(s) from text if any of `start_keys` matches.
        The matching strategy is controlled by `match_strategy` argument in the initialization of `SectionExtractor()`.


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
        # Find all start positions based on strategy
        if self.match_strategy == "greedy":
            start_positions = _find_start_position_greedy_all(
                text, 
                self.start_keys, 
                self.word_boundary, 
                self.flags,
                backend=self.backend,
            )
        else:
            start_positions = _find_start_position_sequential_all(
                text, 
                self.start_keys, 
                self.word_boundary, 
                self.flags,
                backend=self.backend,
            )

        if not start_positions:
            return []

        sections = []

        # Process each start position
        for start_idx_start, start_idx_end in start_positions:
            # Find end position based on strategy
            if self.match_strategy == "greedy":
                end_idx = _find_end_position_greedy(
                    text, 
                    self.end_keys, 
                    start_idx_start, 
                    self.word_boundary, 
                    self.flags,
                    backend=self.backend,
                )
            else:
                end_idx = _find_end_position_sequential(
                    text, 
                    self.end_keys, 
                    start_idx_start, 
                    self.word_boundary, 
                    self.flags,
                    backend=self.backend,
                )

            # Extract the section
            section_start = start_idx_start if self.include_start_keys else start_idx_end
            section = text[section_start:end_idx].strip()

            if section:  # Only add non-empty sections
                sections.append(section)

        return sections