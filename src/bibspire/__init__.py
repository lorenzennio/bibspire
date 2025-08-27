"""
BibSpire: A tool to update .bib entries with INSPIRE-HEP citations
"""

__version__ = "1.0.0"
__author__ = "BibSpire Contributors"
__email__ = "contact@bibspire.org"

from .core import BibSpire, BibEntry, BibParser, InspireAPI
from .cli import main

__all__ = ["BibSpire", "BibEntry", "BibParser", "InspireAPI", "main"]
