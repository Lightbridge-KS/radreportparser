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
from ._pattern import _try_import_re2

def is_re2_available() -> bool:
    """
    Check if the re2 package is available for use.
    
    Returns
    -------
    bool
        True if re2 is installed and available, False otherwise.
    """
    return _try_import_re2() is not None


__all__ = [
    "SectionConfig",
    "RadReportExtractor",
    "KeyWord",
    "RadReport",
    "SectionExtractor",
    "is_re2_available",
    "__version__",
]

__author__ = "Kittipos Sirivongrungson <ki11ip0.s.a.s@gmail.com>"
__version__ = _version("radreportparser")
del _version