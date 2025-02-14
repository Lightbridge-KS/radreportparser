import pytest
import re
from radreportparser.section import (
    _find_start_position,
    _find_end_position_greedy,
    _find_end_position_sequential
)

# Test Data
SAMPLE_TEXT = """EMERGENCY MDCT OF THE BRAIN

HISTORY: A 25-year-old female presents with dizziness
TECHNIQUES: Axial helical scan
COMPARISON: None.
FINDINGS: Normal study
IMPRESSION: No abnormality"""

@pytest.fixture
def sample_text():
    return SAMPLE_TEXT

# Tests for _find_start_position()

def test_find_start_position_basic():
    """Test basic functionality of _find_start_position"""
    text = "FINDINGS: Normal study"
    keys = ["FINDINGS:"]
    start, end = _find_start_position(text, keys)
    assert start == 0
    assert end == 9  # Length of "FINDINGS:"

def test_find_start_position_with_multiple_keys():
    """Test with multiple possible start keys"""
    text = "Clinical History: Patient presents with..."
    
    keys = ["History:", "Clinical History:"]
    start, end = _find_start_position(text, keys, flags=re.IGNORECASE)
    assert start == 0
    assert end == 17  # Length of "Clinical History:"

def test_find_start_position_case_sensitivity():
    """Test case sensitivity settings"""
    text = "findings: Normal study"
    
    # Case sensitive (should not find)
    start, end = _find_start_position(text, ["FINDINGS:"], flags=0)
    assert start == -1
    assert end == -1
    
    # Case insensitive (should find)
    start, end = _find_start_position(text, ["FINDINGS:"], flags=re.IGNORECASE)
    assert start == 0
    assert end == 9

def test_find_start_position_with_none_keys():
    """Test behavior when keys is None"""
    text = "Some text"
    start, end = _find_start_position(text, None)
    assert start == 0
    assert end == 0

def test_find_start_position_no_match():
    """Test when no match is found"""
    text = "Normal study results"
    start, end = _find_start_position(text, ["FINDINGS:"])
    assert start == -1
    assert end == -1

def test_find_start_position_with_word_boundary():
    """Test word boundary behavior"""
    text = "FINDINGSx: Not a real heading"
    
    # Without word boundary (should find with partial match)
    start, end = _find_start_position(text, ["FINDINGS"], word_boundary=False)
    assert start == 0
    assert end == 8
    
    # With word boundary (should not find)
    start, end = _find_start_position(text, ["FINDINGS"], word_boundary=True)
    assert start == -1
    assert end == -1

# Tests for _find_end_position_greedy()

def test_find_end_position_greedy_with_multiple_keys():
    """Test greedy matching with multiple possible end keys"""
    text = "HISTORY: Patient info FINDINGS: Normal IMPRESSION: Clear"
    keys = ["IMPRESSION:", "FINDINGS:"]
    end_pos = _find_end_position_greedy(text, keys, start_pos=0)
    assert end_pos == 22 # Should find first matching key (FINDINGS:)

def test_find_end_position_greedy_no_match():
    """Test when no end position is found"""
    text = "FINDINGS: Normal study"
    keys = ["IMPRESSION:"]
    end_pos = _find_end_position_greedy(text, keys, start_pos=0)
    assert end_pos == len(text)  # Should return end of text

def test_find_end_position_greedy_with_none_keys():
    """Test behavior when keys is None"""
    text = "Some text"
    end_pos = _find_end_position_greedy(text, None, start_pos=0)
    assert end_pos == len(text)

# Tests for _find_end_position_sequential()


def test_find_end_position_sequential_order_matters():
    """Test that sequential matching respects order of keys"""
    text = "HISTORY: Info TECHNIQUES: Details FINDINGS: Normal"
    keys = ["FINDINGS:", "TECHNIQUES:"]  # Order matters
    
    # Should find TECHNIQUES: first (correct order)
    end_pos = _find_end_position_sequential(text, keys[::-1], start_pos=0)
    assert text[end_pos:].startswith("TECHNIQUES:")
    
    # Should find FINDINGS: first (correct order)
    end_pos = _find_end_position_sequential(text, keys, start_pos=0)
    assert text[end_pos:].startswith("FINDINGS:")

def test_find_end_position_sequential_no_match():
    """Test when no end position is found"""
    text = "FINDINGS: Normal study"
    keys = ["IMPRESSION:"]
    end_pos = _find_end_position_sequential(text, keys, start_pos=0)
    assert end_pos == len(text)  # Should return end of text

def test_find_end_position_sequential_with_none_keys():
    """Test behavior when keys is None"""
    text = "Some text"
    end_pos = _find_end_position_sequential(text, None, start_pos=0)
    assert end_pos == len(text)

# Integration Tests with Real Report Format

def test_real_report_section_positions(sample_text):
    """Test position finding with real report format"""
    # Test finding FINDINGS section
    start, end = _find_start_position(sample_text, ["FINDINGS:"])
    assert start >= 0  # Should find FINDINGS
    assert sample_text[start:end].strip() == "FINDINGS:"
    
    # Test finding end of FINDINGS section
    end_pos = _find_end_position_greedy(sample_text, ["IMPRESSION:"], start)
    assert end_pos > start
    assert "IMPRESSION:" in sample_text[end_pos:]

def test_edge_cases():
    """Test various edge cases"""
    # Empty text
    assert _find_start_position("", ["TEST:"]) == (-1, -1)
    assert _find_end_position_greedy("", ["TEST:"], 0) == 0
    assert _find_end_position_sequential("", ["TEST:"], 0) == 0
    
    # Text with only whitespace
    text = "   \n   "
    assert _find_start_position(text, ["TEST:"]) == (-1, -1)
    assert _find_end_position_greedy(text, ["TEST:"], 0) == len(text)
    assert _find_end_position_sequential(text, ["TEST:"], 0) == len(text)
    
    # Invalid start position
    text = "FINDINGS: Test IMPRESSION:"
    assert _find_end_position_greedy(text, ["IMPRESSION:"], len(text)) == len(text)
    assert _find_end_position_sequential(text, ["IMPRESSION:"], len(text)) == len(text)