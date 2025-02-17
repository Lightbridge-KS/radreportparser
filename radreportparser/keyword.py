from enum import Enum

class KeyWord(Enum):
    """Section Keywords for Radiology Reports.
    
    An enumeration class representing different sections commonly found in radiology reports.
    Each enum member contains a list of regular expressions used to match section headers.

    Parameters
    ----------
    None

    Attributes
    ----------
    HISTORY : list of str
        Regular expressions for history/indication sections:
        - Standalone "history"
        - "indication(s)"
        - "clinical history"
        - "clinical indication(s)"
    TECHNIQUE : list of str
        Regular expressions for technique sections:
        - "technique(s)"
    COMPARISON : list of str 
        Regular expressions for comparison sections:
        - "comparison(s)"
    FINDINGS : list of str
        Regular expressions for findings sections:
        - "finding(s)" 
    IMPRESSION : list of str
        Regular expressions for impression sections:
        - "impression(s)"
    FOOTER : list of str
        Regular expressions for footer sections:
        - "Report Severity"
        - "Finalized Datetime" 
        - "Preliminary Datetime"

    Notes
    -----
    - Patterns use `[^\\w\\n]*` to match non-word/non-newline characters before/after keywords
    - `s?` makes pluralization optional (e.g. "finding" or "findings")

    Examples
    --------
    ```{python}
    from radreportparser import KeyWord
    # Get regex patterns for history section
    KeyWord.HISTORY.value
    ```
    """
    HISTORY = [r"[^\w\n]*History[^\w\n]*", r"[^\w\n]*Indications?[^\w\n]*", *[rf"[^\w\n]*clinical\s+{h}[^\w\n]*" for h in ["history", r"indications?"]]]
    TECHNIQUE = [r"[^\w\n]*Techniques?[^\w\n]*"]
    COMPARISON = [r"[^\w\n]*Comparisons?[^\w\n]*"]
    FINDINGS = [r"[^\w\n]*Findings?[^\w\n]*"]
    IMPRESSION = [r"[^\w\n]*Impressions?[^\w\n]*"]
    FOOTER = [r"[^\w\n]*Report Severity[^\w\n]*", r"[^\w\n]*Finalized Datetime[^\w\n]*", r"[^\w\n]*Preliminary Datetime[^\w\n]*"]
