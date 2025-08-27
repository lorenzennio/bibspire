#!/usr/bin/env python3
"""
Allow bibspire to be executed as a module with python -m bibspire
"""

from .cli import main

if __name__ == "__main__":
    main()
