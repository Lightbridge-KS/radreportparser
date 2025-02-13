"""
Example Full Report
"""

from typing import TypedDict
from dataclasses import dataclass, field, asdict

@dataclass
class ExampleReport:
    report_text: str
    truth_study_type: str
    truth_hx_w_key: str
    truth_imp_w_key: str


example_report = {}