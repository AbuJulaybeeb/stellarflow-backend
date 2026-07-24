import struct

from src.serialization.encoders import (
    FLAG_LIVE,
    FRAME_SIZE,
    IPC_TYPE_TELEMETRY_FRAME,
    StructPackEncoder,
    TelemetryFrame,
    pack_frame,
    unpack_frame,
)


def test_packed_struct_layout():
    frame = TelemetryFrame(
        asset_id=b"NGN/XLM",
        price=-123_456_789,
        volume=987_654_321,
        timestamp=1_625_000_000_000,
        sequence=42,
        flags=FLAG_LIVE,
        feed_id=12,
    )

    packed = pack_frame(frame)

    assert FRAME_SIZE == struct.calcsize(">8sqQQIHB")
    assert FRAME_SIZE == 8 + 8 + 8 + 8 + 4 + 2 + 1
    assert len(packed) == FRAME_SIZE == 39
    assert packed == struct.pack(
        ">8sqQQIHB",
        b"NGN/XLM\x00",
        -123_456_789,
        987_654_321,
        1_625_000_000_000,
        42,
        FLAG_LIVE,
        12,
    )
    assert unpack_frame(packed) == frame

    encoder = StructPackEncoder(channel_id=7)
    message = encoder.encode_telemetry_frame(frame)
    header = message[:24]
    payload = message[24:]

    assert len(message) == 24 + FRAME_SIZE
    assert payload == packed
    assert StructPackEncoder.decode_header(header)[:3] == (
        IPC_TYPE_TELEMETRY_FRAME,
        1,
        FRAME_SIZE,
    )
