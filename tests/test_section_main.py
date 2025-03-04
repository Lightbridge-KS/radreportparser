import pytest
import re
from radreportparser import SectionExtractor

# Test Data
MINIMAL_REPORT_TEXT = """EMERGENCY CT BRAIN

HISTORY: 25F, dizziness and LOC

TECHNIQUE: CT brain without contrast

FINDINGS: Normal study
- No hemorrhage
- No mass

IMPRESSION: No acute abnormality"""

MINIMAL_REPORT_MD = """**EMERGENCY CT BRAIN**

**HISTORY:** 25F, dizziness and LOC

**TECHNIQUE:** CT brain without contrast

**FINDINGS:** Normal study
- No hemorrhage
- No mass

**IMPRESSION:** No acute abnormality"""

@pytest.fixture
def report_text():
    return MINIMAL_REPORT_TEXT

@pytest.fixture
def report_md():
    return MINIMAL_REPORT_MD

# Basic Tests with Plain Text Report

def test_extract_section_basic(report_text):
    """Test basic section extraction from plain text"""
    # Extract HISTORY section
    extractor = SectionExtractor(start_keys=["HISTORY:"], end_keys=["TECHNIQUE:"], include_start_keys=True)
    history = extractor.extract(report_text)
    assert history.strip() == "HISTORY: 25F, dizziness and LOC"
    
    # Extract FINDINGS section
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=["IMPRESSION:"], include_start_keys=True)
    findings = extractor.extract(report_text)
    assert "FINDINGS: Normal study" in findings
    assert "No hemorrhage" in findings
    assert "No mass" in findings

def test_extract_section_without_start_key(report_text):
    """Test extraction without including start key"""
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=["IMPRESSION:"], include_start_keys=False)
    findings = extractor.extract(report_text)
    assert not findings.startswith("FINDINGS:")
    assert "Normal study" in findings
    assert "No hemorrhage" in findings

def test_extract_last_section(report_text):
    """Test extracting the last section (no end key)"""
    extractor = SectionExtractor(start_keys=["IMPRESSION:"], end_keys=None, include_start_keys=True)
    impression = extractor.extract(report_text)
    assert impression.strip() == "IMPRESSION: No acute abnormality"

# Tests with Markdown Report

def test_extract_section_markdown(report_md):
    """Test section extraction from markdown formatted text"""
    # Extract HISTORY section
    extractor = SectionExtractor(start_keys=[r"\*\*HISTORY:\*\*"], end_keys=[r"\*\*TECHNIQUE:\*\*"], include_start_keys=True, word_boundary=False)
    history = extractor.extract(report_md)
    assert history.strip() == "**HISTORY:** 25F, dizziness and LOC"
    
    # Extract FINDINGS section with markdown formatting
    extractor = SectionExtractor(start_keys=[r"\*\*FINDINGS:\*\*"], end_keys=[r"\*\*IMPRESSION:\*\*"], include_start_keys=True)
    findings = extractor.extract(report_md)
    assert "**FINDINGS:** Normal study" in findings
    assert "- No hemorrhage" in findings
    assert "- No mass" in findings

def test_word_boundary_behavior():
    """Test word boundary behavior with similar section names"""
    text = """FINDING: No S
FINDINGS_EXTRA: with Extra
FINDINGS: With S
"""
    # Without word boundary
    extractor = SectionExtractor(start_keys=["FINDINGS"], end_keys=None, word_boundary=False)
    result = extractor.extract(text)
    assert "with Extra" in result
    
    # With word boundary
    extractor = SectionExtractor(start_keys=["FINDINGS"], end_keys=None, word_boundary=True)
    result = extractor.extract(text)
    assert "With S" in result

# Test Different Matching Strategies

def test_greedy_vs_sequential_matching():
    """Test difference between greedy and sequential matching"""
    text = """FINDINGS: First finding
TECHNIQUE: Some technique
FINDINGS: Second finding
IMPRESSION: Final impression"""
    
    # Greedy matching (finds first occurrence of any end key)
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=["TECHNIQUE:", "IMPRESSION:"], match_strategy="greedy")
    greedy = extractor.extract(text)
    assert "First finding" in greedy
    assert "Second finding" not in greedy
    
    # Sequential matching (tries end keys in order)
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=["IMPRESSION:", "TECHNIQUE:"], match_strategy="sequential")
    sequential = extractor.extract(text)
    assert "First finding" in sequential
    assert "TECHNIQUE:" in sequential
    assert "Second finding" in sequential

# Edge Cases and Error Handling

def test_empty_and_whitespace():
    """Test behavior with empty and whitespace input"""
    # Empty string
    extractor = SectionExtractor(start_keys=["START:"], end_keys=["END:"])
    assert extractor.extract("") == ""
    
    # Whitespace only
    assert extractor.extract("   \n   ") == ""

def test_invalid_match_strategy():
    """Test error handling for invalid match strategy"""
    with pytest.raises(ValueError):
        SectionExtractor(start_keys=["START:"], end_keys=["END:"], match_strategy="invalid")

def test_no_start_keys():
    """Test extraction from beginning of text (no start keys)"""
    text = "Initial text\nFINDINGS: Some findings"
    extractor = SectionExtractor(start_keys=None, end_keys=["FINDINGS:"], include_start_keys=True)
    result = extractor.extract(text)
    assert result.strip() == "Initial text"

def test_no_end_keys():
    """Test extraction until end of text (no end keys)"""
    text = "FINDINGS: Some findings\nFinal text"
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=None, include_start_keys=True)
    result = extractor.extract(text)
    assert "Some findings" in result
    assert "Final text" in result

def test_case_sensitivity():
    """Test case sensitivity in section extraction"""
    text = """findings: lowercase
FINDINGS: uppercase
Findings: Mixed case"""
    
    # Case sensitive
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=None, flags=0)
    result = extractor.extract(text)
    assert "uppercase" in result
    assert "lowercase" not in result
    
    # Case insensitive
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=None, flags=re.IGNORECASE)
    result = extractor.extract(text)
    assert "lowercase" in result
    assert "uppercase" in result
    assert "Mixed case" in result

def test_multiline_section_content():
    """Test extraction of sections with multiline content"""
    text = """FINDINGS:
Line 1
Line 2
- Bullet point 1
- Bullet point 2

IMPRESSION: End"""
    
    extractor = SectionExtractor(start_keys=["FINDINGS:"], end_keys=["IMPRESSION:"], include_start_keys=True)
    result = extractor.extract(text)
    assert "Line 1" in result
    assert "Line 2" in result
    assert "Bullet point 1" in result
    assert "Bullet point 2" in result
    assert "IMPRESSION:" not in result