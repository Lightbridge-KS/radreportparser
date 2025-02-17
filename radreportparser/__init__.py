"""radreportparser - Regex-based text parser for common radiology report"""

# Change to import.metadata when minimum python>=3.8
from importlib_metadata import version as _version


from .extractor import (
    SectionConfig,
    RadReportExtractor,
)
from .keyword import KeyWord
from .report import RadReport
from .section import (
    SectionExtractor
    )

# __version__ = "0.1.0-alpha.1"


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