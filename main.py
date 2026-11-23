# main.py — entrypoint for the news-image-20261123 entry.
# Runs the renderer in main_src.py and writes the PNG to /output/entry.png
# (falling back to ./output/entry.png when /output is not writable).
# Standard library only, no network, no clock: two runs write identical bytes.

import os
import sys

# The grader runs `python3 -P -s main.py`, which keeps this script's own
# directory off sys.path, so a bare `import main_src` would fail. Put the
# script's directory first, then import the renderer.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main_src


def main():
    png, overflow = main_src.render()
    bad = [name for name, ov in overflow if ov]
    if bad:
        raise SystemExit("text overflow in: " + ", ".join(bad))
    outdir = "/output"
    try:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "entry.png")
        with open(path, "wb") as f:
            f.write(png)
    except OSError:
        outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "output")
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "entry.png")
        with open(path, "wb") as f:
            f.write(png)
    print("wrote %s (%d bytes, %d stories)"
          % (path, len(png), main_src.count_stories()))


if __name__ == "__main__":
    main()
