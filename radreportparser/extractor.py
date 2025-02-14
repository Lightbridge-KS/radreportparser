import re
from dataclasses import dataclass
from typing import List, Optional, Literal

from .keyword import KeyWord
from .section import extract_section


@dataclass
class SectionConfig:
    """# Configuration for a radiology report section.

    Parameters
    ----------
    name : str
        Name of the section (e.g., "history", "findings")
    start_keys : list[str]
        Keys that mark the start of this section
    next_section_keys : list[str] | None
        Keys that mark the start of the next sections
    """

    name: str
    start_keys: List[str] | None
    next_section_keys: Optional[List[str]] = None


class RadReportExtractor:
    """# Extracts sections from radiology reports

    This class provides methods to extract common sections from radiology reports, including:
    - Title section
    - History/Clinical indication
    - Technique/Procedure details  
    - Comparison with prior studies
    - Findings/Description
    - Impression/Conclusion

    Each section is identified by customizable keywords that mark the start and end of sections.

    Parameters
    ----------
    keys_history : list[str], optional
        Keywords that identify the history/clinical section.
        Default uses `KeyWord.HISTORY.value`
    keys_technique : list[str], optional  
        Keywords that identify the technique/procedure section.
        Default uses `KeyWord.TECHNIQUE.value`
    keys_comparison : list[str], optional
        Keywords that identify the comparison section.
        Default uses `KeyWord.COMPARISON.value`
    keys_findings : list[str], optional
        Keywords that identify the findings section.
        Default uses `KeyWord.FINDINGS.value`
    keys_impression : list[str], optional
        Keywords that identify the impression section.
        Default uses `KeyWord.IMPRESSION.value`
    keys_footer : list[str], optional
        Keywords that identify report footer content.
        Default uses `KeyWord.FOOTER.value`

    Methods
    -------
    extract_title(text, include_key=True, word_boundary=False)
        Extract title section from start until first section marker
    extract_history(text, include_key=True, word_boundary=False)
        Extract clinical history/indication section
    extract_technique(text, include_key=True, word_boundary=False)
        Extract procedure technique section
    extract_comparison(text, include_key=True, word_boundary=False)
        Extract comparison with prior studies section
    extract_findings(text, include_key=True, word_boundary=False)
        Extract findings/description section
    extract_impression(text, include_key=True, word_boundary=False)
        Extract impression/conclusion section

    Examples
    --------
    Basic usage with default section markers:

    ```python
    extractor = RadReportExtractor()
    text = '''
    TECHNIQUE: CT scan with contrast
    FINDINGS: Normal chest CT
    IMPRESSION: No acute abnormality
    '''
    findings = extractor.extract_findings(text)
    # Returns: 'FINDINGS: Normal chest CT'
    ```

    Custom section markers:

    ```python
    extractor = RadReportExtractor(
        keys_findings=['DESCRIPTION:', 'FINDINGS:'],
        keys_impression=['CONCLUSION:', 'IMPRESSION:']
    )
    ```

    Notes
    -----
    - Section extraction is case-insensitive by default
    - Returns empty string if section is not found
    - Sections are extracted from their start marker until the next section marker
    - The last matched section continues until end of text
    """
    def __init__(
        self,
        keys_history: list[str] = KeyWord.HISTORY.value,
        keys_technique: list[str] = KeyWord.TECHNIQUE.value,
        keys_comparison: list[str] = KeyWord.COMPARISON.value,
        keys_findings: list[str] = KeyWord.FINDINGS.value,
        keys_impression: list[str] = KeyWord.IMPRESSION.value,
        keys_footer: list[str] = KeyWord.FOOTER.value,
    ):
        self.section_configs = {
            "title": SectionConfig(
                name="title",
                start_keys=None,
                next_section_keys=[
                    *keys_history,
                    *keys_technique,
                    *keys_comparison,
                    *keys_findings,
                    *keys_impression,
                ],
            ),
            "history": SectionConfig(
                name="history",
                start_keys=keys_history,
                next_section_keys=[
                    *keys_technique,
                    *keys_comparison,
                    *keys_findings,
                    *keys_impression,
                ],
            ),
            "technique": SectionConfig(
                name="technique",
                start_keys=keys_technique,
                next_section_keys=[*keys_comparison, *keys_findings, *keys_impression],
            ),
            "comparison": SectionConfig(
                name="comparison",
                start_keys=keys_comparison,
                next_section_keys=[*keys_technique, *keys_findings, *keys_impression],
            ),
            "findings": SectionConfig(
                name="findings",
                start_keys=keys_findings,
                next_section_keys=[*keys_impression, *keys_footer],
            ),
            "impression": SectionConfig(
                name="impression",
                start_keys=keys_impression,
                next_section_keys=keys_footer,
            ),
        }

    def _extract_section_base(
        self,
        text: str,
        start_keys: list[str] | None,
        next_section_keys: list[str] | None,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Base method for extracting sections from radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text
        start_keys : list[str]
            List of possible section start markers
        next_section_keys : list[str] | None
            List of possible next section markers that would end the current section
        include_key : bool
            Whether to include the section key in output
        word_boundary : bool
            Whether to wrap word boundary around the section keys
        flags : re.RegexFlag
            Regex flags to use in pattern matching
        match_strategy : {"greedy", "sequential"}
            Strategy for matching end keys

        Returns
        -------
        str
            The extracted section text. Returns empty string if section not found.
        """

        return extract_section(
            text,
            start_keys=start_keys,
            end_keys=next_section_keys,
            include_start_keys=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )

    def _extract_section_by_name(
        self,
        text: str,
        section_name: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Extract a section by name from the radiology report text.
        """
        config = self.section_configs.get(section_name)
        if not config:
            raise ValueError(f"Unknown section: {section_name}")

        return self._extract_section_base(
            text,
            start_keys=config.start_keys,
            next_section_keys=config.next_section_keys,
            include_key=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )
        
    def extract_title(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Extract the title section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the section keys, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"

        Returns
        -------
        str
            The extracted title section text. Returns empty string if section not found.
        """
        return self._extract_section_by_name(
            text,
            "title",
            include_key=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )

    def extract_history(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Extract the history/indication section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the section keys, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"

        Returns
        -------
        str
            The extracted history section text. Returns empty string if section not found.
        """
        return self._extract_section_by_name(
            text,
            "history",
            include_key=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )

    def extract_technique(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Extract the technique section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the section keys, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"

        Returns
        -------
        str
            The extracted technique section text. Returns empty string if section not found.
        """
        return self._extract_section_by_name(
            text,
            "technique",
            include_key=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )

    def extract_comparison(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Extract the comparison section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the section keys, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"

        Returns
        -------
        str
            The extracted comparison section text. Returns empty string if section not found.
        """
        return self._extract_section_by_name(
            text,
            "comparison",
            include_key=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )

    def extract_findings(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Extract the findings section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the section keys, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"

        Returns
        -------
        str
            The extracted findings section text. Returns empty string if section not found.
        """
        return self._extract_section_by_name(
            text,
            "findings",
            include_key=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )

    def extract_impression(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
    ) -> str:
        """Extract the impression section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the section keys, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"

        Returns
        -------
        str
            The extracted impression section text. Returns empty string if section not found.
        """
        return self._extract_section_by_name(
            text,
            "impression",
            include_key=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
        )

