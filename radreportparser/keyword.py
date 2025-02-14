from enum import Enum

class KeyWord(Enum):
    """
    An enumeration class representing different sections commonly found in radiology reports.
    Each enum member contains a list of regular expressions used to match section headers.
    Members:
        HISTORY (list): Regular expressions for matching history/indication sections
            - Matches standalone "history"
            - Matches "indication(s)"
            - Matches "clinical history" 
            - Matches "clinical indication(s)"
        TECHNIQUE (list): Regular expressions for matching technique sections
            - Matches "technique(s)"
        COMPARISON (list): Regular expressions for matching comparison sections
            - Matches "comparison(s)"
        FINDINGS (list): Regular expressions for matching findings sections
            - Matches "Finding(s)"
        IMPRESSION (list): Regular expressions for matching impression sections
            - Matches "Impression(s)"
        FOOTER (list): Regular expressions for matching footer sections
            - Matches "Report Severity"
            - Matches "Finalized Datetime"
            - Matches "Preliminary Datetime"
    Note:
        - All patterns use non-word and non-newline character matching (`[^\w\n]*`) to match any non-word characters before and after the keyword.
        - (s?) makes the 's' optional to match both singular and plural forms
    """
    HISTORY = [r"[^\w\n]*History[^\w\n]*", r"[^\w\n]*Indication(s?)[^\w\n]*", *[rf"[^\w\n]*clinical\s+{h}[^\w\n]*" for h in ["history", r"indication(s?)"]]]
    TECHNIQUE = [r"[^\w\n]*Technique(s?)[^\w\n]*"]
    COMPARISON = [r"[^\w\n]*Comparison(s?)[^\w\n]*"]
    FINDINGS = [r"[^\w\n]*Finding(s?)[^\w\n]*"]
    IMPRESSION = [r"[^\w\n]*Impression(s?)[^\w\n]*"]
    FOOTER = [r"[^\w\n]*Report Severity[^\w\n]*", r"[^\w\n]*Finalized Datetime[^\w\n]*", r"[^\w\n]*Preliminary Datetime[^\w\n]*"]
