"""
BibSpire: A tool to update .bib entries with INSPIRE-HEP citations
"""

__version__ = "1.0.0"
__author__ = "BibSpire Contributors"
__email__ = "contact@bibspire.org"

from .cli import main
from .core import BibEntry, BibParser, BibSpire, InspireAPI

__all__ = ["BibSpire", "BibEntry", "BibParser", "InspireAPI", "main"]
