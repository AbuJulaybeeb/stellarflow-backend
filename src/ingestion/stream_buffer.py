"""stream_buffer.py — zero-copy JSON stream parser using memoryview.

Accepts raw network binary blocks and locates newline-delimited JSON frames
without allocating intermediate string objects, reducing GC pressure during
high-volume market-volatility spikes.
"""
from __future__ import annotations

import json
from typing import Any, Generator

_NEWLINE = ord("\n")
_DEFAULT_BUFFER_SIZE = 64 * 1024


class StreamBuffer:
    """Accumulate binary chunks and yield parsed JSON objects zero-copy."""

    __slots__ = ("_buf", "_start", "_size", "_capacity")

    def __init__(self, buffer_size: int = _DEFAULT_BUFFER_SIZE) -> None:
        if buffer_size <= 0:
            raise ValueError("buffer size must be positive")
        self._buf = bytearray(buffer_size)
        self._start = 0
        self._size = 0
        self._capacity = buffer_size

    def _compact(self) -> None:
        """Move any retained bytes back to the front of the backing buffer."""
        if self._size == 0 or self._start == 0:
            return
        view = memoryview(self._buf)[self._start : self._start + self._size]
        self._buf[: self._size] = view
        self._start = 0

    def feed(self, data: bytes | bytearray | memoryview) -> Generator[Any, None, None]:
        """Append *data* and yield every complete newline-delimited JSON frame.

        The parser uses a pre-allocated backing buffer that is reused across feeds
        so stream workers avoid repeated dynamic allocations for incoming blocks.
        """
        if not data:
            return

        payload = memoryview(data)
        self._compact()

        if len(payload) > self._capacity - self._size:
            raise ValueError("stream chunk exceeds pre-allocated buffer capacity")

        end = self._start + self._size
        self._buf[end : end + len(payload)] = payload
        self._size += len(payload)

        limit = self._start + self._size
        cursor = self._start

        while True:
            pos = self._buf.find(b'\n', cursor, limit)
            if pos == -1:
                break
            if pos > cursor:
                frame_view = memoryview(self._buf)[cursor:pos]
                yield json.loads(frame_view)
            cursor = pos + 1

        consumed = cursor - self._start

        if consumed:
            self._start += consumed
            self._size -= consumed
            if self._size == 0:
                self._start = 0

    def reset(self) -> None:
        """Discard all buffered data while keeping the backing storage reusable."""
        self._start = 0
        self._size = 0


__all__ = ["StreamBuffer"]
