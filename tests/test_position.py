import pytest
import re
from radreportparser._position import (
    _find_start_position_greedy,
    _find_start_position_sequential,
    _find_start_position_greedy_all,
    _find_start_position_sequential_all,
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

# Tests for _find_start_position_greedy()

def test_find_start_position_greedy_basic():
    """Test basic functionality of greedy start position finding"""
    text = "FINDINGS: Normal study"
    keys = ["FINDINGS:"]
    start, end = _find_start_position_greedy(text, keys)
    assert start == 0
    assert end == 9  # Length of "FINDINGS:"

def test_find_start_position_greedy_with_multiple_keys():
    """Test greedy matching with multiple possible start keys"""
    text = "Clinical History: Patient presents with..."
    keys = ["History:", "Clinical History:"]
    start, end = _find_start_position_greedy(text, keys, flags=re.IGNORECASE)
    assert start == 0
    assert end == 17  # Length of "Clinical History:"

# Tests for _find_start_position_sequential()

def test_find_start_position_sequential_basic():
    """Test basic functionality of sequential start position finding"""
    text = "FINDINGS: Normal study"
    keys = ["FINDINGS:"]
    start, end = _find_start_position_sequential(text, keys)
    assert start == 0
    assert end == 9

def test_find_start_position_sequential_order_matters():
    """Test that sequential matching respects order of keys"""
    text = "AAA BBB"
    
    # Order: specific -> general
    keys = ["BBB", "AAA"]
    start, end = _find_start_position_sequential(text, keys, flags=re.IGNORECASE)
    assert end == 7  # Should match "Clinical History:"
    

# Tests for _find_start_position_greedy_all()

def test_find_start_position_greedy_all_basic():
    """Test finding all start positions with greedy matching"""
    text = """FINDINGS: First finding
    FINDINGS: Second finding
    FINDINGS: Third finding"""
    
    positions = _find_start_position_greedy_all(text, ["FINDINGS:"])
    assert len(positions) == 3
    assert all(text[start:end].strip() == "FINDINGS:" for start, end in positions)

def test_find_start_position_greedy_all_multiple_patterns():
    """Test finding all positions with multiple patterns"""
    text = """FINDING: First
    FINDINGS: Second
    FINDING: Third"""
    
    positions = _find_start_position_greedy_all(text, ["FINDING:", "FINDINGS:"])
    assert len(positions) == 3

# Tests for _find_start_position_sequential_all()

def test_find_start_position_sequential_all_basic():
    """Test finding all start positions with sequential matching"""
    text = """FINDINGS: First finding
    FINDINGS: Second finding"""
    
    positions = _find_start_position_sequential_all(text, ["FINDINGS:"])
    assert len(positions) == 2
    assert all(text[start:end].strip() == "FINDINGS:" for start, end in positions)

def test_find_start_position_sequential_all_order():
    """Test that sequential all respects pattern order"""
    text = """AAA: First
    BBB: Second
    AAA: Third"""
    
    # Order: specific -> general
    positions = _find_start_position_sequential_all(
        text,
        ["BBB:", "AAA:"],
        flags=re.IGNORECASE
    )
    print(positions)
    assert len(positions) == 3
    
    # Order should be maintained in document order
    assert positions == sorted(positions)

# Common cases for all start position functions

def test_start_position_case_sensitivity():
    """Test case sensitivity settings for all start position functions"""
    text = "findings: Normal study"
    
    # Case sensitive (should not find)
    for func in [_find_start_position_greedy, _find_start_position_sequential]:
        start, end = func(text, ["FINDINGS:"], flags=0)
        assert start == -1
        assert end == -1
    
    # Case insensitive (should find)
    for func in [_find_start_position_greedy, _find_start_position_sequential]:
        start, end = func(text, ["FINDINGS:"], flags=re.IGNORECASE)
        assert start == 0
        assert end == 9

def test_start_position_with_none_keys():
    """Test behavior when keys is None for all start position functions"""
    text = "Some text"
    
    # Single position functions
    for func in [_find_start_position_greedy, _find_start_position_sequential]:
        start, end = func(text, None)
        assert start == 0
        assert end == 0
    
    # Multiple position functions
    for func in [_find_start_position_greedy_all, _find_start_position_sequential_all]:
        positions = func(text, None)
        assert positions == [(0, 0)]

def test_start_position_no_match():
    """Test when no match is found for all start position functions"""
    text = "Normal study results"
    
    # Single position functions
    for func in [_find_start_position_greedy, _find_start_position_sequential]:
        start, end = func(text, ["FINDINGS:"])
        assert start == -1
        assert end == -1
    
    # Multiple position functions
    for func in [_find_start_position_greedy_all, _find_start_position_sequential_all]:
        positions = func(text, ["FINDINGS:"])
        assert positions == []

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
    start, end = _find_start_position_greedy(sample_text, ["FINDINGS:"])
    assert start >= 0  # Should find FINDINGS
    assert sample_text[start:end].strip() == "FINDINGS:"
    
    # Test finding end of FINDINGS section
    end_pos = _find_end_position_greedy(sample_text, ["IMPRESSION:"], start)
    assert end_pos > start
    assert "IMPRESSION:" in sample_text[end_pos:]

def test_edge_cases():
    """Test various edge cases"""
    # Empty text
    assert _find_start_position_greedy("", ["TEST:"]) == (-1, -1)
    assert _find_end_position_greedy("", ["TEST:"], 0) == 0
    assert _find_end_position_sequential("", ["TEST:"], 0) == 0
    
    # Text with only whitespace
    text = "   \n   "
    assert _find_start_position_greedy(text, ["TEST:"]) == (-1, -1)
    assert _find_end_position_greedy(text, ["TEST:"], 0) == len(text)
    assert _find_end_position_sequential(text, ["TEST:"], 0) == len(text)
    
    # Invalid start position
    text = "FINDINGS: Test IMPRESSION:"
    assert _find_end_position_greedy(text, ["IMPRESSION:"], len(text)) == len(text)
    assert _find_end_position_sequential(text, ["IMPRESSION:"], len(text)) == len(text)