from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json

@dataclass
class RadReport:
    """A dataclass representing a radiology report with its various sections.

    This class holds the different sections commonly found in radiology reports,
    including title, clinical history, technique, comparison with prior studies,
    findings, and impression.

    Parameters
    ----------
    title : str, optional
        The title or header section of the report
    history : str, optional
        The clinical history or indication section
    technique : str, optional
        The imaging technique or procedure details section
    comparison : str, optional
        The comparison with prior studies section
    findings : str, optional
        The radiological findings or description section
    impression : str, optional
        The impression or conclusion section

    Examples
    --------
    >>> report = RadReport(
    ...     title="CT BRAIN WITHOUT CONTRAST",
    ...     history="25F with headache",
    ...     findings="Normal brain parenchyma",
    ...     impression="No acute intracranial abnormality"
    ... )
    >>> report.to_dict()
    {
        'title': 'CT BRAIN WITHOUT CONTRAST',
        'history': '25F with headache',
        'findings': 'Normal brain parenchyma',
        'impression': 'No acute intracranial abnormality',
        'technique': None,
        'comparison': None
    }
    """
    title: Optional[str] = None
    history: Optional[str] = None
    technique: Optional[str] = None
    comparison: Optional[str] = None
    findings: Optional[str] = None
    impression: Optional[str] = None

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        """Convert the RadReport to a dictionary.

        This method converts the RadReport object to a dictionary format.

        Parameters
        ----------
        exclude_none : bool, optional
            If True, excludes keys with None values from the output dictionary.
            If False, includes all keys (default).

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the report sections as key-value pairs.

        Examples
        --------
        >>> report = RadReport(title="CT BRAIN", findings="Normal")
        >>> report.to_dict()
        {'title': 'CT BRAIN', 'history': None, 'technique': None,
         'comparison': None, 'findings': 'Normal', 'impression': None}
        >>> report.to_dict(exclude_none=True)
        {'title': 'CT BRAIN', 'findings': 'Normal'}
        """
        d = asdict(self)
        if exclude_none:
            return {k: v for k, v in d.items() if v is not None}
        return d

    def to_json(self, exclude_none: bool = False, **kwargs) -> str:
        """Convert the RadReport to a JSON string.

        Similar to pandas DataFrame.to_json(), this method converts
        the RadReport object to a JSON formatted string.

        Parameters
        ----------
        exclude_none : bool, optional
            If True, excludes keys with None values from the output JSON.
            If False, includes all keys (default).
        **kwargs : dict
            Additional keyword arguments to pass to json.dumps().
            Common options include:
            - indent: int, for pretty printing
            - sort_keys: bool, to sort keys alphabetically

        Returns
        -------
        str
            A JSON string representation of the report.

        Examples
        --------
        >>> report = RadReport(title="CT BRAIN", findings="Normal")
        >>> print(report.to_json(indent=2))
        {
          "title": "CT BRAIN",
          "history": null,
          "technique": null,
          "comparison": null,
          "findings": "Normal",
          "impression": null
        }
        >>> print(report.to_json(exclude_none=True))
        {"title":"CT BRAIN","findings":"Normal"}
        """
        return json.dumps(self.to_dict(exclude_none=exclude_none), **kwargs)


