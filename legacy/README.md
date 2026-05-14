# Legacy scripts

These are the original scripts I wrote while first studying steganography. They only handle pure 2-color (black & white) message images, and the approach is much more limited than the current version at the repo root — but they were the starting point so they're preserved here.

## The idea

The message image must be 2 colors. The encoder counts both colors in the message, picks the **less common** one, finds where that color appears in the message, and replaces the corresponding pixels in the cover with that same color. Extraction reverses the process. The message dimensions are smuggled in the cover's last two pixels (e.g. `480x270` is broken into `04, 80, 02, 70` across six channel slots).

The trick relies on the cover already containing the color you're injecting — for example, hiding white message pixels works best if the cover is full of `(254, 254, 254)` so the injected `(255, 255, 255)` is visually indistinguishable. That's what `genImage.py` was for.

## Files

| File | Purpose |
|---|---|
| `steg.py` | Hide / extract entry point. Usage: `python steg.py -h` |
| `genImage.py` | Generate a solid-color image. `python genImage.py <r> <g> <b> <name>` |
| `count_pixels.py` | Count black vs. white pixels. `python count_pixels.py <image>` |
| `two_color_check.py` | Test whether an image is exactly 2 colors. `python two_color_check.py <image>` |

## Requirements

```bash
pip install pillow
```
