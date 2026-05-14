"""Smoke test: encode a message into a cover, decode it back, verify it matches."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw

import steg


def _make_cover(path: Path, size: tuple[int, int] = (128, 96)) -> None:
    """A random-noise RGB cover image."""
    rng = random.Random(42)
    pixels = bytes(rng.randrange(256) for _ in range(size[0] * size[1] * 3))
    Image.frombytes("RGB", size, pixels).save(path, format="PNG")


def _make_message(path: Path, size: tuple[int, int] = (128, 96)) -> None:
    """A simple white-background message with a black rectangle in the middle."""
    img = Image.new("L", size, color=255)
    draw = ImageDraw.Draw(img)
    draw.rectangle((30, 20, 90, 70), fill=0)
    img.save(path, format="PNG")


def test_encode_decode_roundtrip(tmp_path: Path) -> None:
    cover = tmp_path / "cover.png"
    message = tmp_path / "message.png"
    stego_path = tmp_path / "stego.png"
    revealed = tmp_path / "revealed.png"

    _make_cover(cover)
    _make_message(message)

    steg.encode(str(cover), str(message), str(stego_path), n=5)
    steg.decode(str(stego_path), str(revealed), n=5)

    original_mask = steg.binarize(Image.open(message).convert("L"))
    revealed_img = Image.open(revealed).convert("L")
    revealed_mask = revealed_img.point(lambda v: 255 if v < 128 else 0)

    orig_bytes = original_mask.tobytes()
    rev_bytes = revealed_mask.tobytes()
    assert len(orig_bytes) == len(rev_bytes)
    matches = sum(1 for a, b in zip(orig_bytes, rev_bytes) if a == b)
    accuracy = matches / len(orig_bytes)
    assert accuracy > 0.99, f"Round-trip accuracy {accuracy:.4f} below threshold"


def test_stego_visually_close_to_cover(tmp_path: Path) -> None:
    """The stego image should differ from the cover by only a few bits per channel."""
    cover = tmp_path / "cover.png"
    message = tmp_path / "message.png"
    stego_path = tmp_path / "stego.png"

    _make_cover(cover)
    _make_message(message)

    threshold = 5
    steg.encode(str(cover), str(message), str(stego_path), n=threshold)

    cover_bytes = Image.open(cover).convert("RGB").tobytes()
    stego_bytes = Image.open(stego_path).convert("RGB").tobytes()

    bits = steg.bit_depth_for_threshold(threshold)
    max_change = (1 << bits) - 1
    max_diff = max(abs(a - b) for a, b in zip(cover_bytes, stego_bytes))
    assert max_diff <= max_change, f"max per-channel change {max_diff} exceeded {max_change}"
