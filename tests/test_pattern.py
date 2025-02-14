from radreportparser.pattern import _pattern_keys
import re
import pytest


def test_pattern_keys_basic_matching():
    """Test basic pattern matching functionality"""
    # Single word
    pattern = _pattern_keys(['history'])
    assert pattern.search('history')
    assert pattern.search('HISTORY')
    assert not pattern.search('hist')
    
    # Regex Markdown Match
    pattern = _pattern_keys([r'\W*finding(s?)\W*'], word_boundary=False)
    assert pattern.search('**Finding:**')
    assert pattern.search('**Finding\n:**')


def test_pattern_keys_word_boundary():
    """Test word boundary behavior"""
    # With word boundary (default)
    pattern = _pattern_keys(['hist'])
    assert pattern.search('hist:')
    
    ## Not match whole word
    assert not pattern.search('hhist')
    assert not pattern.search('histttt')
    assert not pattern.search('hhhisttt')
    ## Markdown Will Match
    assert pattern.search('**hist:**')
    
    # Without word boundary
    pattern = _pattern_keys(['hist'], word_boundary=False)
    assert pattern.search('hhhisttt')

def test_pattern_keys_error():
    """Test Error Handling"""
    # Empty list
    with pytest.raises(ValueError):
        _pattern_keys([])


def test_pattern_keys_regex():
    """Test Regex"""
    # Non-charater keys
    pattern = _pattern_keys([r'\W+'], word_boundary=False)
    assert pattern.search('+')
    assert pattern.search(':')
    assert pattern.search('*')
    assert pattern.search(' ')
