"""Format conversion. process() was renamed to transform() in 2.0."""

from pathlib import Path

FORMATS = ("csv", "json", "parquet")


def transform(source: str, output_format: str = "json", output: str | None = None) -> Path:
    """Convert source to output_format and return the path written."""
    if output_format not in FORMATS:
        raise ValueError(f"output_format must be one of {FORMATS}")
    target = Path(output) if output else Path(source).with_suffix(f".{output_format}")
    # Conversion itself is omitted from this fixture.
    return target
