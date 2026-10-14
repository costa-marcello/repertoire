#!/usr/bin/env python3
"""Compute WCAG 2.x contrast ratios for text/background colour pairs.

Usage:
    python contrast.py FG BG [FG BG ...] [--min RATIO]

Colours are hex: #rgb, #rrggbb, or #rrggbbaa. The leading # is optional; when
it is present, quote the colour ('#1a1a1a'), because shells treat an unquoted
# as the start of a comment. For a translucent foreground, append the CSS
alpha after a slash (f5f0e8/0.7 or f5f0e8/70%); this is exact, while the two
alpha digits of #rrggbbaa round to 1/255 steps. A foreground with alpha is
blended over its background before measuring. A background must be opaque,
because what lies behind it is unknown.

Prints one line per pair, then a summary line:
    #8fa3b8 on #11202f  6.37:1  PASS (min 4.5)
    RESULT pairs=<n> failed=<n> min=<ratio>

The ratio is compared unrounded, so 4.499 fails a 4.5 minimum, as WCAG requires.
Use --min 3 for large text (24px, or 18.66px bold), focus rings, and input
borders.

Exit codes: 0 every pair meets the minimum, 1 at least one pair fails,
2 usage error (odd number of colours, bad hex, translucent background).
Standard library only; no network.
"""

from __future__ import annotations

import argparse
import re
import sys

HEX = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?:/(\d*\.?\d+)(%?))?$")


def parse_hex(text: str) -> tuple[float, float, float, float]:
    """Return (r, g, b, a) in 0-1 from #rgb, #rrggbb, #rrggbbaa, or any of them with /alpha."""
    match = HEX.match(text.strip())
    if not match:
        raise ValueError(f"'{text}' is not a hex colour (#rgb, #rrggbb, #rrggbbaa, optionally followed by /0.7 or /70%)")
    digits, alpha_text, percent = match.groups()
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    channels = [int(digits[i:i + 2], 16) / 255 for i in range(0, len(digits), 2)]
    if len(channels) == 3:
        channels.append(1.0)
    if alpha_text is not None:
        if len(digits) == 8:
            raise ValueError(f"'{text}' gives alpha twice; use #rrggbb/alpha or #rrggbbaa, not both")
        alpha = float(alpha_text) / (100 if percent else 1)
        if not 0 <= alpha <= 1:
            raise ValueError(f"alpha in '{text}' must be between 0 and 1 (or 0% and 100%)")
        channels[3] = alpha
    return channels[0], channels[1], channels[2], channels[3]


def blend(fg: tuple[float, float, float, float], bg: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Composite a possibly translucent foreground over an opaque background."""
    alpha = fg[3]
    return tuple(fg[i] * alpha + bg[i] * (1 - alpha) for i in range(3))


def luminance(rgb: tuple[float, float, float]) -> float:
    """WCAG relative luminance of an sRGB colour with channels in 0-1."""
    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg_text: str, bg_text: str) -> float:
    """Contrast ratio of fg over bg, from 1.0 to 21.0."""
    fg = parse_hex(fg_text)
    bg = parse_hex(bg_text)
    if bg[3] < 1.0:
        raise ValueError(f"background '{bg_text}' is translucent; pass the opaque colour it renders as")
    lighter, darker = sorted((luminance(blend(fg, bg)), luminance(bg[:3])), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="WCAG contrast ratios for FG BG hex pairs.")
    parser.add_argument("colours", nargs="+", metavar="FG BG", help="foreground and background hex colours, in pairs")
    parser.add_argument("--min", type=float, default=4.5, dest="minimum",
                        help="minimum ratio to pass (default 4.5 for body text; 3 for large text, focus rings, and input borders)")
    args = parser.parse_args(argv)

    if len(args.colours) % 2:
        print("error: colours must come in FG BG pairs; got an odd number. "
              "Quote colours that start with # so the shell does not drop them as a comment.", file=sys.stderr)
        return 2

    pairs = list(zip(args.colours[0::2], args.colours[1::2]))
    failed = 0
    for fg_text, bg_text in pairs:
        try:
            value = ratio(fg_text, bg_text)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        verdict = "PASS" if value >= args.minimum else "FAIL"
        failed += verdict == "FAIL"
        print(f"{fg_text} on {bg_text}  {value:.2f}:1  {verdict} (min {args.minimum:g})")

    print(f"RESULT pairs={len(pairs)} failed={failed} min={args.minimum:g}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
