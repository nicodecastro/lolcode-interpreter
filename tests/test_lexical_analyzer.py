import pytest
import src.lexical_analyzer as lexical_analyzer

def test_get_lexemes():
    result = lexical_analyzer.get_lexemes("hello world!")
    assert result == "hello world!"