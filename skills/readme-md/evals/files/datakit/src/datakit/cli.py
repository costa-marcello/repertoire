"""Command line: datakit convert <file> --to <format> [--out <file>]."""

import argparse

from datakit.core import FORMATS, transform


def main() -> None:
    parser = argparse.ArgumentParser(prog="datakit")
    commands = parser.add_subparsers(dest="command", required=True)
    convert = commands.add_parser("convert", help="convert a file to another format")
    convert.add_argument("source")
    convert.add_argument("--to", choices=FORMATS, required=True)
    convert.add_argument("--out")
    args = parser.parse_args()
    print(transform(args.source, output_format=args.to, output=args.out))
