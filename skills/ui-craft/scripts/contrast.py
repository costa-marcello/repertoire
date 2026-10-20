#!/usr/bin/env python3
"""Compute WCAG 2.x contrast ratios for text/background colour pairs.

Usage:
    python contrast.py FG BG [FG BG ...] [--min RATIO]

Colours are hex (#rgb, #rrggbb, #rrggbbaa) or CSS rgb(), hsl(), or oklch(),
so values from Tailwind v4 and shadcn/ui themes can be passed as written.
Wrap bare shadcn HSL channels as hsl(222 47% 11%). Quote every colour: shells
treat an unquoted # as the start of a comment, and the functions contain
spaces and parentheses. The leading # of a hex colour is optional.

For a translucent foreground, give its CSS alpha: after a slash for hex
(f5f0e8/0.7 or f5f0e8/70%; exact, while the two alpha digits of #rrggbbaa
round to 1/255 steps), or inside the function (oklch(0.97 0.01 80 / 0.7)).
A foreground with alpha is blended over its background before measuring.
A background must be opaque, because what lies behind it is unknown.

An oklch() colour outside sRGB is clipped to it and named in a note on stderr;
its ratio is then approximate, because wide-gamut screens show it unclipped.

Prints one line per pair, then a summary line:
    #8fa3b8 on #11202f  6.37:1  PASS (min 4.5)
    RESULT pairs=<n> failed=<n> min=<ratio>

The ratio is compared unrounded, so 4.499 fails a 4.5 minimum, as WCAG requires.
Use --min 3 for large text (24px, or 18.66px bold), focus rings, and input
borders.

Exit codes: 0 every pair meets the minimum, 1 at least one pair fails,
2 usage error (odd number of colours, unreadable colour, translucent background).
Standard library only; no network.
"""

from __future__ import annotations

import argparse
import colorsys
import math
import re
import sys
from typing import Tuple

HEX = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?:/(\d*\.?\d+)(%?))?$")
FUNCTION = re.compile(r"^(rgba?|hsla?|oklch)\(([^()]*)\)$", re.IGNORECASE)
NUMBER = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)(%|deg)?$", re.IGNORECASE)
FORMATS = ("hex (#rgb, #rrggbb, #rrggbbaa, optionally followed by /0.7 or /70%), "
           "rgb(), hsl(), or oklch()")

Colour = Tuple[float, float, float, float]


def parse_hex(text: str) -> Colour | None:
    """Return (r, g, b, a) in 0-1 from #rgb, #rrggbb, #rrggbbaa, or any of them with /alpha; None if not hex."""
    match = HEX.match(text)
    if not match:
        return None
    digits, alpha_text, percent = match.groups()
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    channels = [int(digits[i:i + 2], 16) / 255 for i in range(0, len(digits), 2)]
    if len(channels) == 3:
        channels.append(1.0)
    if alpha_text is not None:
        if len(digits) == 8:
            raise ValueError(f"'{text}' gives alpha twice; use #rrggbb/alpha or #rrggbbaa, not both")
        channels[3] = check_alpha(float(alpha_text) / (100 if percent else 1), text)
    return channels[0], channels[1], channels[2], channels[3]


def check_alpha(alpha: float, text: str) -> float:
    if not 0 <= alpha <= 1:
        raise ValueError(f"alpha in '{text}' must be between 0 and 1 (or 0% and 100%)")
    return alpha


def component(token: str, text: str) -> tuple[float, str]:
    """Return (value, unit) for one function argument; the unit is '', '%', or 'deg'."""
    if token.lower() == "none":
        return 0.0, ""
    match = NUMBER.match(token)
    if not match:
        raise ValueError(f"'{token}' in '{text}' is not a number")
    return float(match.group(1)), (match.group(2) or "").lower()


def scaled(value: float, unit: str, full: float, percent_full: float = 100.0) -> float:
    """Scale a component to 0-1 of its range: a plain number out of `full`, a percentage out of 100%."""
    return value / (percent_full if unit == "%" else full)


def oklch_to_srgb(lightness: float, chroma: float, hue: float) -> tuple[tuple[float, float, float], bool]:
    """Convert OKLCH to gamma-encoded sRGB in 0-1; also return whether it had to be clipped."""
    a = chroma * math.cos(math.radians(hue))
    b = chroma * math.sin(math.radians(hue))
    l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    linear = (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )
    clipped = any(c < -1e-4 or c > 1 + 1e-4 for c in linear)

    def encode(c: float) -> float:
        c = min(max(c, 0.0), 1.0)
        return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

    r, g, b_ = (encode(c) for c in linear)
    return (r, g, b_), clipped


def parse_function(text: str) -> Colour | None:
    """Return (r, g, b, a) in 0-1 from rgb(), hsl(), or oklch() in modern or comma syntax; None if not one."""
    match = FUNCTION.match(text)
    if not match:
        return None
    name, body = match.group(1).lower().rstrip("a"), match.group(2)
    alpha_token = None
    if "," in body:
        tokens = [t.strip() for t in body.split(",")]
        if len(tokens) == 4:
            alpha_token = tokens.pop()
    else:
        colour_part, _, alpha_part = body.partition("/")
        tokens = colour_part.split()
        alpha_token = alpha_part.strip() or None
    if len(tokens) != 3:
        raise ValueError(f"'{text}' needs three components")
    (v1, u1), (v2, u2), (v3, u3) = (component(t, text) for t in tokens)

    alpha = 1.0
    if alpha_token is not None:
        value, unit = component(alpha_token, text)
        alpha = check_alpha(scaled(value, unit, 1.0), text)

    if name == "rgb":
        rgb = tuple(min(max(scaled(v, u, 255.0), 0.0), 1.0) for v, u in ((v1, u1), (v2, u2), (v3, u3)))
    elif name == "hsl":
        rgb = colorsys.hls_to_rgb((v1 % 360) / 360, min(max(v3 / 100, 0.0), 1.0), min(max(v2 / 100, 0.0), 1.0))
    else:
        lightness = min(max(scaled(v1, u1, 1.0), 0.0), 1.0)
        chroma = max(scaled(v2, u2, 1.0, percent_full=250.0), 0.0)  # 100% chroma is 0.4
        rgb, clipped = oklch_to_srgb(lightness, chroma, v3 % 360)
        if clipped:
            print(f"note: '{text}' lies outside sRGB and was clipped, so its ratio is approximate", file=sys.stderr)
    return rgb[0], rgb[1], rgb[2], alpha


def parse_colour(text: str) -> Colour:
    """Return (r, g, b, a) in 0-1 from any supported colour format."""
    cleaned = text.strip()
    colour = parse_hex(cleaned) or parse_function(cleaned)
    if colour is None:
        raise ValueError(f"'{text}' is not a colour; use {FORMATS}")
    return colour


def blend(fg: Colour, bg: Colour) -> tuple[float, float, float]:
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
    fg = parse_colour(fg_text)
    bg = parse_colour(bg_text)
    if bg[3] < 1.0:
        raise ValueError(f"background '{bg_text}' is translucent; pass the opaque colour it renders as")
    lighter, darker = sorted((luminance(blend(fg, bg)), luminance(bg[:3])), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="WCAG contrast ratios for FG BG colour pairs (hex, rgb(), hsl(), oklch()).")
    parser.add_argument("colours", nargs="+", metavar="FG BG", help="foreground and background colours, in pairs")
    parser.add_argument("--min", type=float, default=4.5, dest="minimum",
                        help="minimum ratio to pass (default 4.5 for body text; 3 for large text, focus rings, and input borders)")
    args = parser.parse_args(argv)

    if len(args.colours) % 2:
        print("error: colours must come in FG BG pairs; got an odd number. Quote every colour: "
              "the shell drops an unquoted # as a comment and splits a function at its spaces.", file=sys.stderr)
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
