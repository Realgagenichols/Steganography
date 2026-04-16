# Steganography

Hide a message image inside a cover image using low-bit threshold steganography.

## How It Works

1. **Encode**: The lowest few bits of each pixel channel are manipulated. Non-message pixels have their low bits normalized to be >= threshold `n`. For message foreground pixels, one channel's low bits are set just below `n`. The maximum change per channel is small (e.g., 7 for the default threshold of 5), making the modification imperceptible.

2. **Decode**: Any pixel where at least one channel's low bits fall below `n` is identified as a message pixel, producing a black-on-white binary image.

## Setup

```bash
uv sync
```

## Usage

### Encode (hide a message)

```bash
uv run steg encode --cover photo.jpg --message secret.png --output stego.png
```

### Decode (extract the message)

```bash
uv run steg decode --input stego.png --output revealed.png
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--threshold` | `-n` | 5 | Low-bit threshold. Higher values use more bits (slightly more visible but more robust). |

Output **must** be `.png` — lossy formats like JPEG will destroy the hidden data.

## Examples

```bash
# Encode with default threshold (5)
uv run steg encode -c landscape.jpg -m logo.png -o hidden.png

# Encode with lower threshold (more subtle, 1-bit depth)
uv run steg encode -c landscape.jpg -m logo.png -o hidden.png -n 2

# Decode
uv run steg decode -i hidden.png -o extracted.png

# Decode with matching threshold
uv run steg decode -i hidden.png -o extracted.png -n 2
```

## How the Message Image Is Interpreted

- The message is converted to grayscale then binarized at a brightness cutoff of 128
- **Dark pixels** (< 128) = foreground (the hidden content)
- **Light pixels** (>= 128) = background (ignored)
- The message is resized to match the cover image dimensions
