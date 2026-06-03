import pytest
from src.core.hashid import encode_id, decode_id

def test_encode_id():
    result = encode_id(123)
    assert isinstance(result, str)
    assert len(result) > 0

def test_decode_id():
    encoded = encode_id(123)
    decoded = decode_id(encoded)
    assert decoded == 123

def test_decode_id_invalid():
    result = decode_id("invalid_hash")
    assert result is None