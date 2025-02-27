"""radreportparser - Regex-based text parser for common radiology report"""

from importlib.metadata import version as _version


from .extractor import (
    SectionConfig,
    RadReportExtractor,
)
from .keyword import KeyWord
from .report import RadReport
from .section import (
    SectionExtractor
    )



__all__ = [
    "SectionConfig",
    "RadReportExtractor",
    "KeyWord",
    "RadReport",
    "SectionExtractor",
    "__version__",
]

__author__ = "Kittipos Sirivongrungson <ki11ip0.s.a.s@gmail.com>"
__version__ = _version("radreportparser")
del _version