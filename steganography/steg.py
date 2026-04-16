"""Threshold-based image steganography.

Hides a message image inside a cover image by manipulating the lowest bits
of pixel channel values relative to a threshold. The cover is normalized so
the low bits of all channels >= n, then message foreground pixels get one
channel's low bits reduced below n. Extraction checks for any channel whose
low bits fall below n.

Because only the lowest few bits are modified, the maximum change per channel
is small (e.g., 7 for 3-bit depth), making the hidden message imperceptible.
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
from pathlib import Path

from PIL import Image

DEFAULT_THRESHOLD = 5
BINARIZE_CUTOFF = 128

logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


def bit_depth_for_threshold(n: int) -> int:
    """Return the number of low bits needed to represent threshold n."""
    return max(math.ceil(math.log2(n + 1)), 1)


def binarize(grayscale: Image.Image) -> Image.Image:
    """Convert a grayscale image to a binary mask (mode 'L', values 0 or 255).

    Dark pixels (< BINARIZE_CUTOFF) become 255 (foreground).
    Light pixels become 0 (background).
    """
    return grayscale.point(lambda v: 255 if v < BINARIZE_CUTOFF else 0)


def encode(cover_path: str, message_path: str, output_path: str, n: int) -> None:
    """Encode a message image into a cover image.

    Works by manipulating only the lowest `bit_depth` bits of each channel:
    - Non-message pixels: low bits are normalized to >= n
    - Message pixels: one channel's low bits are set to n-1 (below threshold)

    Maximum change per channel = (2^bit_depth - 1), ensuring imperceptibility.
    """
    bits = bit_depth_for_threshold(n)
    mask = (1 << bits) - 1

    log.info("Loading cover image: %s", cover_path)
    cover = Image.open(cover_path).convert("RGB")

    log.info("Loading message image: %s", message_path)
    message = Image.open(message_path).convert("L")

    # Resize message to match cover dimensions
    if message.size != cover.size:
        log.info(
            "Resizing message from %dx%d to %dx%d",
            message.width, message.height, cover.width, cover.height,
        )
        message = message.resize(cover.size, Image.Resampling.LANCZOS)

    # Binarize: dark pixels become foreground (255), light become background (0)
    msg_mask = binarize(message)
    mask_bytes = msg_mask.tobytes()

    cover_bytes = bytearray(cover.tobytes())
    num_pixels = cover.width * cover.height
    embedded_count = 0

    log.info(
        "Encoding (threshold=%d, bit_depth=%d, max_change=%d)...",
        n, bits, mask,
    )

    sentinel = n - 1  # value to embed in low bits for message pixels

    for i in range(num_pixels):
        base = i * 3
        r = cover_bytes[base]
        g = cover_bytes[base + 1]
        b = cover_bytes[base + 2]

        # Extract low bits
        r_low = r & mask
        g_low = g & mask
        b_low = b & mask

        if mask_bytes[i]:  # message foreground pixel
            # Pick the channel whose low bits are closest to sentinel (n-1)
            # to minimize the visual change
            diffs = [abs(r_low - sentinel), abs(g_low - sentinel), abs(b_low - sentinel)]
            best = diffs.index(min(diffs))

            # Set that channel's low bits to sentinel (below threshold)
            if best == 0:
                cover_bytes[base] = (r & ~mask) | sentinel
            elif best == 1:
                cover_bytes[base + 1] = (g & ~mask) | sentinel
            else:
                cover_bytes[base + 2] = (b & ~mask) | sentinel

            # Normalize the OTHER two channels (low bits >= n)
            for c, low in [(base, r_low), (base + 1, g_low), (base + 2, b_low)]:
                if c == base + best:
                    continue  # skip the embedded channel
                if low < n:
                    cover_bytes[c] = (cover_bytes[c] & ~mask) | n

            embedded_count += 1
        else:
            # Non-message pixel: normalize all channels (low bits >= n)
            if r_low < n:
                cover_bytes[base] = (r & ~mask) | n
            if g_low < n:
                cover_bytes[base + 1] = (g & ~mask) | n
            if b_low < n:
                cover_bytes[base + 2] = (b & ~mask) | n

    result = Image.frombytes("RGB", cover.size, bytes(cover_bytes))
    result.save(output_path, format="PNG")

    total = num_pixels
    pct = embedded_count / total * 100
    log.info(
        "Embedded %d/%d pixels (%.1f%%) into %s",
        embedded_count, total, pct, output_path,
    )


def decode(input_path: str, output_path: str, n: int) -> None:
    """Decode a hidden message from a stego image.

    Any pixel where at least one channel's low bits are < n is a message pixel.
    """
    bits = bit_depth_for_threshold(n)
    mask = (1 << bits) - 1

    log.info("Loading stego image: %s", input_path)
    stego = Image.open(input_path).convert("RGB")
    stego_bytes = stego.tobytes()

    num_pixels = stego.width * stego.height
    out_bytes = bytearray(b"\xff" * num_pixels * 3)  # start with white
    found_count = 0

    log.info("Extracting message (threshold=%d, bit_depth=%d)...", n, bits)
    for i in range(num_pixels):
        base = i * 3
        r = stego_bytes[base]
        g = stego_bytes[base + 1]
        b = stego_bytes[base + 2]

        if (r & mask) < n or (g & mask) < n or (b & mask) < n:
            out_bytes[base] = 0
            out_bytes[base + 1] = 0
            out_bytes[base + 2] = 0
            found_count += 1

    result = Image.frombytes("RGB", stego.size, bytes(out_bytes))
    result.save(output_path, format="PNG")

    log.info("Extracted %d message pixels to %s", found_count, output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="steg",
        description="Threshold-based image steganography — hides a message image "
        "inside a cover image by manipulating low-order bits.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # encode
    enc = sub.add_parser("encode", help="Hide a message image inside a cover image")
    enc.add_argument("--cover", "-c", required=True, help="Path to the cover image")
    enc.add_argument("--message", "-m", required=True, help="Path to the message image")
    enc.add_argument("--output", "-o", required=True, help="Output path (.png)")
    enc.add_argument(
        "--threshold", "-n", type=int, default=DEFAULT_THRESHOLD,
        help=f"Low-bit threshold (default: {DEFAULT_THRESHOLD}). "
        "Higher = more bit depth used, slightly more visible but more robust.",
    )

    # decode
    dec = sub.add_parser("decode", help="Extract the hidden message from a stego image")
    dec.add_argument("--input", "-i", required=True, help="Path to the stego image")
    dec.add_argument("--output", "-o", required=True, help="Output path for revealed message (.png)")
    dec.add_argument(
        "--threshold", "-n", type=int, default=DEFAULT_THRESHOLD,
        help=f"Threshold used during encoding (default: {DEFAULT_THRESHOLD})",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Validate threshold
    if args.threshold < 2:
        parser.error("Threshold must be >= 2")
    if args.threshold > 128:
        parser.error("Threshold must be <= 128")

    bits = bit_depth_for_threshold(args.threshold)
    max_change = (1 << bits) - 1
    if max_change > 15:
        log.warning(
            "Threshold %d requires %d-bit depth (max change per channel: %d). "
            "Changes may be noticeable.",
            args.threshold, bits, max_change,
        )

    # Validate output format
    output_path = Path(args.output)
    if output_path.suffix.lower() != ".png":
        parser.error(
            f"Output must be a .png file (got '{output_path.suffix}'). "
            "Lossy formats like JPEG will destroy the hidden message."
        )

    if args.command == "encode":
        for path, label in [(args.cover, "Cover"), (args.message, "Message")]:
            if not Path(path).is_file():
                parser.error(f"{label} image not found: {path}")
        encode(args.cover, args.message, str(output_path), args.threshold)

    elif args.command == "decode":
        if not Path(args.input).is_file():
            parser.error(f"Input image not found: {args.input}")
        decode(args.input, str(output_path), args.threshold)


if __name__ == "__main__":
    main()
