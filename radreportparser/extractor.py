import re
from dataclasses import dataclass
from typing import List, Optional, Literal, Union

from .keyword import KeyWord
from .report import RadReport
from .section import SectionExtractor


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
    backend : {"re", "re2"}, optional
        Regex backend to use:
        - "re": Standard Python regex engine (default)
        - "re2": Google's RE2 engine (must be installed)

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

    ```{python}
    extractor = RadReportExtractor()
    text = '''
    TECHNIQUE: CT scan with contrast
    FINDINGS: Normal chest CT
    IMPRESSION: No acute abnormality
    '''
    findings = extractor.extract_findings(text)
    findings
    ```

    Custom section markers:

    ```{python}
    extractor = RadReportExtractor(
        keys_findings=['DESCRIPTION:', 'FINDINGS:'],
        keys_impression=['CONCLUSION:', 'IMPRESSION:']
    )
    extractor
    ```

    Using re2 backend:

    ```{python}
    extractor = RadReportExtractor(backend="re2")
    findings = extractor.extract_findings(text)
    findings
    ```

    Notes
    -----
    - Section extraction is case-insensitive by default
    - Returns empty string if section is not found
    - Sections are extracted from their start marker until the next section marker
    - The last matched section continues until end of text
    - If using the "re2" backend, you must have the re2 package installed
    """
    def __init__(
        self,
        keys_history: list[str] = KeyWord.HISTORY.value,
        keys_technique: list[str] = KeyWord.TECHNIQUE.value,
        keys_comparison: list[str] = KeyWord.COMPARISON.value,
        keys_findings: list[str] = KeyWord.FINDINGS.value,
        keys_impression: list[str] = KeyWord.IMPRESSION.value,
        keys_footer: list[str] = KeyWord.FOOTER.value,
        backend: Literal["re", "re2"] = "re",
    ):
        self.backend = backend
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
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
        flags : Union[re.RegexFlag, int]
            Regex flags to use in pattern matching.
            For 're' backend: These are directly passed to re.compile()
            For 're2' backend: These are converted to re2.Options properties
        match_strategy : {"greedy", "sequential"}
            Strategy for matching end keys
        verbose : bool, optional
            If True, prints messages if multiple start matches are found.
            Default is True.

        Returns
        -------
        str
            The extracted section text. Returns empty string if section not found.
        """
        extractor = SectionExtractor(
            start_keys=start_keys,
            end_keys=next_section_keys,
            include_start_keys=include_key,
            word_boundary=word_boundary,
            flags=flags,
            match_strategy=match_strategy,
            backend=self.backend,
        )
        return extractor.extract(text, verbose=verbose)

    def _extract_section_by_name(
        self,
        text: str,
        section_name: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
            verbose=verbose,
        )

    def extract_all(
        self,
        text: str,
        include_key: bool = False,
        **kwargs,
    ) -> RadReport:
        """Extract all sections from the radiology report text.

        This is the top-level method for the `RadReportExtractor()` class. It extracts all available sections 
        from the input text and returns them in a `RadReport()` object.

        Parameters
        ----------
        text : str
            The input radiology report text
        include_key : bool, optional
            Whether to include section keys in output, by default False
        **kwargs
            Parameters passed to all child functions

        Returns
        -------
        RadReport
            A RadReport object containing all extracted sections

        Examples
        --------
        
        ```{python}
        from radreportparser import RadReportExtractor
        
        extractor = RadReportExtractor()
        
        text = '''
        EMERGENCY MDCT OF THE BRAIN

        HISTORY: 25-year-old female presents with headache. Physical examination reveals no focal neurological deficits.

        TECHNIQUE: Axial helical scan of the brain performed using 2.5-mm (brain) and 1.25-mm (bone) slice thickness with coronal and sagittal reconstructions.

        COMPARISON: None.

        FINDINGS:
        Cerebral parenchyma: Age-appropriate brain volume with normal parenchymal attenuation and gray-white differentiation. No acute large territorial infarction or intraparenchymal hemorrhage identified.

        Cerebellum and posterior fossa: Normal.

        Extraaxial spaces: No extra-axial collection.

        Ventricles: Normal size. No intraventricular hemorrhage.

        Midline shift: None.

        Brain herniation: None.

        Vascular system: Normal.

        Calvarium and scalp: No fracture identified.

        Skull base, sella and temporomandibular joints (TMJs): Normal.

        Visualized orbits, paranasal sinuses and mastoid air cells: Unremarkable.

        Visualized upper cervical spine: No fracture identified.

        IMPRESSION:
        - No intracranial hemorrhage, acute large territorial infarction, extra-axial collection, midline shift, brain herniation, or skull fracture identified.
        '''
        
        report = extractor.extract_all(text)
        report
        ```
        
        ### Report by Element

        
        ```{python}
        report.title
        ```
        
        ```{python}
        report.history
        ```
        
        ```{python}
        report.impression
        ```
        
        ### Convert to dictionary
        
        ```{python}
        report.to_dict()
        ```
        
        ### Convert to JSON
        
        ```{python}
        report.to_json()
        ```
        """
        return RadReport(
            title=self.extract_title(
                text,
                **kwargs,
            ),
            history=self.extract_history(
                text,
                include_key=include_key,
                **kwargs,
            ),
            technique=self.extract_technique(
                text,
                include_key=include_key,
                **kwargs,
            ),
            comparison=self.extract_comparison(
                text,
                include_key=include_key,
                **kwargs,
            ),
            findings=self.extract_findings(
                text,
                include_key=include_key,
                **kwargs,
            ),
            impression=self.extract_impression(
                text,
                include_key=include_key,
                **kwargs,
            ),
        )
    def extract_title(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
        flags : Union[re.RegexFlag, int], optional
            Regex flags to use in pattern matching.
            For 're' backend: These are directly passed to re.compile()
            For 're2' backend: These are converted to re2.Options properties
            By default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"
        verbose : bool, optional
            If True, prints messages if multiple start matches are found.
            Default is True.

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
            verbose=verbose,
        )

    def extract_history(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
        flags : Union[re.RegexFlag, int], optional
            Regex flags to use in pattern matching.
            For 're' backend: These are directly passed to re.compile()
            For 're2' backend: These are converted to re2.Options properties
            By default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"
        verbose : bool, optional
            If True, prints messages if multiple start matches are found.
            Default is True.

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
            verbose=verbose,
        )

    def extract_technique(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
        flags : Union[re.RegexFlag, int], optional
            Regex flags to use in pattern matching.
            For 're' backend: These are directly passed to re.compile()
            For 're2' backend: These are converted to re2.Options properties
            By default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"
        verbose : bool, optional
            If True, prints messages if multiple start matches are found.
            Default is True.

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
            verbose=verbose,
        )

    def extract_comparison(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
        flags : Union[re.RegexFlag, int], optional
            Regex flags to use in pattern matching.
            For 're' backend: These are directly passed to re.compile()
            For 're2' backend: These are converted to re2.Options properties
            By default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"
        verbose : bool, optional
            If True, prints messages if multiple start matches are found.
            Default is True.

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
            verbose=verbose,
        )

    def extract_findings(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
        flags : Union[re.RegexFlag, int], optional
            Regex flags to use in pattern matching.
            For 're' backend: These are directly passed to re.compile()
            For 're2' backend: These are converted to re2.Options properties
            By default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"
        verbose : bool, optional
            If True, prints messages if multiple start matches are found.
            Default is True.

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
            verbose=verbose,
        )

    def extract_impression(
        self,
        text: str,
        include_key: bool = True,
        word_boundary: bool = False,
        flags: Union[re.RegexFlag, int] = re.IGNORECASE,
        match_strategy: Literal["greedy", "sequential"] = "greedy",
        verbose: bool = True,
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
        flags : Union[re.RegexFlag, int], optional
            Regex flags to use in pattern matching.
            For 're' backend: These are directly passed to re.compile()
            For 're2' backend: These are converted to re2.Options properties
            By default re.IGNORECASE
        match_strategy : {"greedy", "sequential"}, optional
            Strategy for matching end keys:
            - "greedy": Use first matching end key (faster)
            - "sequential": Try end keys in order (more precise)
            Default is "greedy"
        verbose : bool, optional
            If True, prints messages if multiple start matches are found.
            Default is True.

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
            verbose=verbose,
        )