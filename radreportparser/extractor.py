import re
from typing import List

from .keyword import KeyWord
from .section import extract_section
from .pattern import _get_first_key_match


class RadReportExtractor:
    """# Extracting sections from radiology reports.
    
    This class provides methods to extract different sections commonly found in radiology
    reports, such as history, technique, comparison, findings, and impression sections.
    Each section is identified by specific keywords that can be customized during initialization.
    
    keys_history : list[str], optional
        List of keywords that identify the history section, defaults to KeyWord.HISTORY.value
    keys_technique : list[str], optional
        List of keywords that identify the technique section, defaults to KeyWord.TECHNIQUE.value
    keys_comparison : list[str], optional
        List of keywords that identify the comparison section, defaults to KeyWord.COMPARISON.value
    keys_findings : list[str], optional
        List of keywords that identify the findings section, defaults to KeyWord.FINDINGS.value
    keys_impression : list[str], optional
        List of keywords that identify the impression section, defaults to KeyWord.IMPRESSION.value
    keys_footer : list[str], optional
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
        keys_history: list[str] = KeyWord.HISTORY.value,
        keys_technique: list[str] = KeyWord.TECHNIQUE.value,
        keys_comparison: list[str] = KeyWord.COMPARISON.value,
        keys_findings: list[str] = KeyWord.FINDINGS.value,
        keys_impression: list[str] = KeyWord.IMPRESSION.value,
        keys_footer: list[str] = KeyWord.FOOTER.value,
    ):
        self.keys_history = keys_history
        self.keys_technique = keys_technique
        self.keys_comparison = keys_comparison
        self.keys_findings = keys_findings
        self.keys_impression = keys_impression
        self.keys_footer = keys_footer

    def extract_title(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = True,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the title section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the `start_keys` and `end_keys`.
            Default is True.
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted title section text. Returns empty string if section not found.
        """

        other_keys = [
            *self.keys_history,
            *self.keys_technique,
            *self.keys_comparison,
            *self.keys_findings,
            *self.keys_impression,
        ]
        title_section = extract_section(
            text,
            start_keys=None, # Extract from the beginning
            end_keys=other_keys,
            include_start_keys=include_key,
            word_boundary = word_boundary,
            flags=flags,
        )


        return title_section


    def extract_history(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = True,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the history/indication section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the `start_keys` and `end_keys`.
            Default is True.
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted history section text. Returns empty string if section not found.
        """
        
        start_key_matched = _get_first_key_match(
            text, keys=self.keys_history, word_boundary = word_boundary
        )

        if start_key_matched:
            # Start key is matched, extract the history section
            other_keys = [
                *self.keys_technique,
                *self.keys_comparison,
                *self.keys_findings,
                *self.keys_impression,
            ]
            history_section = extract_section(
                text,
                start_keys=self.keys_history,
                end_keys=other_keys,
                include_start_keys=include_key,
                word_boundary = word_boundary,
                flags=flags,
            )
        else:
            history_section = ""

        return history_section

    def extract_technique(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = True,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the technique section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the `start_keys` and `end_keys`.
            Default is True.
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted technique section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.keys_technique, word_boundary = word_boundary
        )

        if start_key_matched:
            # Start key is matched, extract the technique section
            other_keys = [
                *self.keys_comparison,
                *self.keys_findings,
                *self.keys_impression,
            ]
            technique_section = extract_section(
                text,
                start_keys=self.keys_technique,
                end_keys=other_keys,
                include_start_keys=include_key,
                word_boundary = word_boundary,
                flags=flags,
            )
        else:
            technique_section = ""
        return technique_section

    def extract_comparison(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = True,
        flags: re.RegexFlag = re.IGNORECASE,
    ):
        """Extract the comparison section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the `start_keys` and `end_keys`.
            Default is True.
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted comparison section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.keys_comparison, word_boundary = word_boundary
        )

        if start_key_matched:
            # Start key is matched, extract the comparison section
            other_keys = [*self.keys_technique, *self.keys_findings, *self.keys_impression]
            comparison_section = extract_section(
                text,
                start_keys=self.keys_comparison,
                end_keys=other_keys,
                include_start_keys=include_key,
                word_boundary = word_boundary,
                flags=flags,
            )
        else:
            comparison_section = ""
        return comparison_section

    def extract_findings(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = True,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the findings section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the `start_keys` and `end_keys`.
            Default is True.
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted findings section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.keys_findings, word_boundary = word_boundary
        )

        if start_key_matched:
            # Start key is matched, extract the findings section
            other_keys = [*self.keys_impression, *self.keys_footer]
            findings_section = extract_section(
                text,
                start_keys=self.keys_findings,
                end_keys=other_keys,
                include_start_keys=include_key,
                word_boundary = word_boundary,
                flags=flags,
            )
        else:
            findings_section = ""

        return findings_section

    def extract_impression(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = True,
        flags: re.RegexFlag = re.IGNORECASE,
    ) -> str:
        """Extract the impression section from the radiology report text.

        Parameters
        ----------
        text : str
            The input radiology report text.
        include_key : bool, optional
            Whether to include the section key in output, by default True
        word_boundary : bool, optional
            Whether to wrap word boundary `\b` around the `start_keys` and `end_keys`.
            Default is True.
        flags : re.RegexFlag, optional
            Regex flags to use in pattern matching, by default re.IGNORECASE

        Returns
        -------
        str
            The extracted impression section text. Returns empty string if section not found.
        """
        start_key_matched = _get_first_key_match(
            text, keys=self.keys_impression, word_boundary = word_boundary
        )

        if start_key_matched:
            # Start key is matched, extract the impression section
            # Since impression is typically the last section, we pass None as end_keys
            impression_section = extract_section(
                text,
                start_keys=self.keys_impression,
                end_keys=self.keys_footer,
                include_start_keys=include_key,
                word_boundary = word_boundary,
                flags=flags,
            )
        else:
            impression_section = ""

        return impression_section




def remove_footer():
    raise NotImplementedError("Not implemented yet")
