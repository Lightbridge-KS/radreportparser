import re
from typing import List

from .keyword import KeyWord
from .section import extract_section
from .pattern import _get_first_key_match


class RadReportParser:
    """A parser class for extracting sections from radiology reports.
    This class provides methods to extract different sections commonly found in radiology
    reports, such as history, technique, comparison, findings, and impression sections.
    Each section is identified by specific keywords that can be customized during initialization.
    
    key_history : list[str], optional
        List of keywords that identify the history section, defaults to KeyWord.HISTORY.value
    key_technique : list[str], optional
        List of keywords that identify the technique section, defaults to KeyWord.TECHNIQUE.value
    key_comparison : list[str], optional
        List of keywords that identify the comparison section, defaults to KeyWord.COMPARISON.value
    key_findings : list[str], optional
        List of keywords that identify the findings section, defaults to KeyWord.FINDINGS.value
    key_impression : list[str], optional
        List of keywords that identify the impression section, defaults to KeyWord.IMPRESSION.value
    key_footer : list[str], optional
        List of keywords that identify the footer section, defaults to KeyWord.FOOTER.value
    Methods
    extract_history(text: str, include_key: bool = True, regex: bool = False, flags: re.RegexFlag = re.IGNORECASE) -> str
        Extract the history section from the report text.
    extract_technique(text: str, include_key: bool = True, regex: bool = False, flags: re.RegexFlag = re.IGNORECASE) -> str
        Extract the technique section from the report text.
    extract_comparison(text: str, include_key: bool = True, regex: bool = False, flags: re.RegexFlag = re.IGNORECASE) -> str
        Extract the comparison section from the report text.
    extract_findings(text: str, include_key: bool = True, regex: bool = False, flags: re.RegexFlag = re.IGNORECASE) -> str
        Extract the findings section from the report text.
    extract_impression(text: str, include_key: bool = True, regex: bool = False, flags: re.RegexFlag = re.IGNORECASE) -> str
        Extract the impression section from the report text.
    remove_footer()
        Remove the footer section from the report text.
    Examples
    --------
    >>> parser = RadReportParser()
    >>> text = '''HISTORY: Patient presents with chest pain
    ... TECHNIQUE: CT scan with contrast
    ... FINDINGS: Normal chest CT
    ... IMPRESSION: No acute abnormality'''
    >>> parser.extract_findings(text)
    'FINDINGS: Normal chest CT'
    """

    def __init__(
        self,
        key_history: list[str] = KeyWord.HISTORY.value,
        key_technique: list[str] = KeyWord.TECHNIQUE.value,
        key_comparison: list[str] = KeyWord.COMPARISON.value,
        key_findings: list[str] = KeyWord.FINDINGS.value,
        key_impression: list[str] = KeyWord.IMPRESSION.value,
        key_footer: list[str] = KeyWord.FOOTER.value,
    ):
        self.key_history = key_history
        self.key_technique = key_technique
        self.key_comparison = key_comparison
        self.key_findings = key_findings
        self.key_impression = key_impression
        self.key_footer = key_footer

    def extract_history(
        self,
        text: str,
        include_key: bool = True,
        regex: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the history/indication section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        regex : bool, optional
            Whether to treat keys as regex patterns, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted history section text. Returns empty string if section not found.
        """
        
        start_key_matched = _get_first_key_match(
            text, keys=self.key_history, regex=regex
        )

        if start_key_matched:
            # Start key is matched, extract the history section
            other_keys = [
                *self.key_technique,
                *self.key_comparison,
                *self.key_findings,
                *self.key_impression,
            ]
            history_section = extract_section(
                text,
                start_keys=self.key_history,
                end_keys=other_keys,
                include_start_keys=include_key,
                regex=regex,
                flags=flags,
            )
        else:
            history_section = ""

        return history_section

    def extract_technique(
        self,
        text: str,
        include_key: bool = True,
        regex: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the technique section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        regex : bool, optional
            Whether to treat keys as regex patterns, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted technique section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.key_technique, regex=regex
        )

        if start_key_matched:
            # Start key is matched, extract the technique section
            other_keys = [
                *self.key_comparison,
                *self.key_findings,
                *self.key_impression,
            ]
            technique_section = extract_section(
                text,
                start_keys=self.key_technique,
                end_keys=other_keys,
                include_start_keys=include_key,
                regex=regex,
                flags=flags,
            )
        else:
            technique_section = ""
        return technique_section

    def extract_comparison(
        self,
        text: str,
        include_key: bool = True,
        regex: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
    ):
        """Extract the comparison section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        regex : bool, optional
            Whether to treat keys as regex patterns, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted comparison section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.key_comparison, regex=regex
        )

        if start_key_matched:
            # Start key is matched, extract the comparison section
            other_keys = [*self.key_technique, *self.key_findings, *self.key_impression]
            comparison_section = extract_section(
                text,
                start_keys=self.key_comparison,
                end_keys=other_keys,
                include_start_keys=include_key,
                regex=regex,
                flags=flags,
            )
        else:
            comparison_section = ""
        return comparison_section

    def extract_findings(
        self,
        text: str,
        include_key: bool = True,
        regex: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the findings section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        regex : bool, optional
            Whether to treat keys as regex patterns, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted findings section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.key_findings, regex=regex
        )

        if start_key_matched:
            # Start key is matched, extract the findings section
            other_keys = [*self.key_impression, *self.key_footer]
            findings_section = extract_section(
                text,
                start_keys=self.key_findings,
                end_keys=other_keys,
                include_start_keys=include_key,
                regex=regex,
                flags=flags,
            )
        else:
            findings_section = ""

        return findings_section

    def extract_impression(
        self,
        text: str,
        include_key: bool = True,
        regex: bool = False,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the impression section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        regex : bool, optional
            Whether to treat keys as regex patterns, by default False
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted impression section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.key_impression, regex=regex
        )

        if start_key_matched:
            # Start key is matched, extract the impression section
            # Since impression is typically the last section, we pass None as end_keys
            impression_section = extract_section(
                text,
                start_keys=self.key_impression,
                end_keys=self.key_footer,
                include_start_keys=include_key,
                regex=regex,
                flags=flags,
            )
        else:
            impression_section = ""

        return impression_section

    def remove_footer(self):
        pass
