from tsa_service import (
    decode_tsr,
    encode_tsr,
)


def test_tsr_base64_roundtrip():
    raw = b"\x30\x03abc"

    stored = encode_tsr(raw)

    assert decode_tsr(
        stored
    ) == raw


def test_legacy_hex_decode():
    raw = b"\x30" + b"x" * 80

    assert decode_tsr(
        raw.hex()
    ) == raw
