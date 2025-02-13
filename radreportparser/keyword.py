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
        - All patterns use non-word character matching (\\W*) which will match `[^a-zA-Z0-9_]`.
        - (s?) makes the 's' optional to match both singular and plural forms
    """
    
    HISTORY = [r"\W*history\W*", r"\W*indication(s?)\W*", *[rf"\W*clinical\s+{h}\W*" for h in ["history", r"indication(s?)"]]]
    TECHNIQUE = [r"\W*technique(s?)\W*"]
    COMPARISON = [r"\W*comparison(s?)\W*"]
    FINDINGS = [r"\W*Finding(s?)\W*"]
    IMPRESSION = [r"\W*Impression(s?)\W*"]
    FOOTER = [r"\W*Report Severity\W*", r"\W*Finalized Datetime\W*", r"\W*Preliminary Datetime\W*"]
