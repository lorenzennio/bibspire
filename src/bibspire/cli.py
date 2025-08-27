#!/usr/bin/env python3
"""
Command-line interface for BibSpire
"""

import argparse
import sys

from .core import BibSpire


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Update .bib file entries with INSPIRE-HEP citations",
        prog="bibspire",
        epilog="Example: bibspire input.bib -o output.bib -v",
    )
    parser.add_argument("input_file", help="Input .bib file")
    parser.add_argument(
        "-o", "--output", help="Output .bib file (defaults to input file)"
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests in seconds (default: 1.0)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    try:
        bibspire = BibSpire(delay=args.delay, verbose=args.verbose)
        bibspire.update_bib_file(args.input_file, args.output)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
