#!/usr/bin/env python3
"""
Core BibSpire functionality
"""

import re
import time
from typing import Dict, List, Optional

import requests


class InspireAPI:
    """Interface to INSPIRE-HEP API"""

    BASE_URL = "https://inspirehep.net/api"

    def __init__(self, delay: float = 1.0):
        """
        Initialize INSPIRE API client

        Args:
            delay: Delay between API requests in seconds
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "BibSpire/1.0 (https://github.com/user/bibspire)"}
        )

    def search_literature(self, query: str) -> Optional[Dict]:
        """
        Search INSPIRE literature database

        Args:
            query: Search query string

        Returns:
            First matching record or None if no match found
        """
        try:
            url = f"{self.BASE_URL}/literature"
            params = {"q": query, "format": "json", "size": 1}

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get("hits", {}).get("total", 0) > 0:
                return data["hits"]["hits"][0]
            return None

        except Exception as e:
            print(f"Error searching INSPIRE: {e}")
            return None
        finally:
            time.sleep(self.delay)

    def get_bibtex(self, record_id: str) -> Optional[str]:
        """
        Get BibTeX citation for a record

        Args:
            record_id: INSPIRE record ID

        Returns:
            BibTeX string or None if error
        """
        try:
            url = f"{self.BASE_URL}/literature/{record_id}"
            params = {"format": "bibtex"}

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            return response.text.strip()

        except Exception as e:
            print(f"Error getting BibTeX for record {record_id}: {e}")
            return None
        finally:
            time.sleep(self.delay)


class BibEntry:
    """Represents a single bibliographic entry"""

    def __init__(self, entry_type: str, key: str, fields: Dict[str, str]):
        self.entry_type = entry_type
        self.key = key
        self.fields = fields

    def to_bibtex(self) -> str:
        """Convert entry back to BibTeX format"""
        lines = [f"@{self.entry_type}{{{self.key},"]

        for field, value in self.fields.items():
            lines.append(f"  {field} = {{{value}}},")

        lines.append("}")
        return "\n".join(lines)

    def get_search_query(self) -> str:
        """Generate search query for INSPIRE"""
        # Priority order: DOI > eprint > title+author > title only

        # DOI is most specific and reliable
        if "doi" in self.fields:
            doi = self.fields["doi"].strip("{}")
            if doi:
                return f"doi:{doi}"

        # eprint/arXiv ID is also very specific
        if "eprint" in self.fields:
            eprint = self.fields["eprint"].strip("{}")
            if eprint:
                return f"eprint:{eprint}"

        # Combine title and author for better specificity
        if "title" in self.fields and "author" in self.fields:
            title = self.fields["title"].strip("{}")
            author = self.fields["author"].strip("{}")
            # Extract first author
            first_author = author.split(" and ")[0].strip()
            if title and first_author:
                return f'title:"{title}" and author:"{first_author}"'

        # Title only as last resort, but only if it's reasonably specific
        if "title" in self.fields:
            title = self.fields["title"].strip("{}")
            # Only use title if it's long enough to be specific (avoid matching common phrases)
            if title and len(title.split()) >= 5:
                return f'title:"{title}"'

        return ""

    def matches_result(self, inspire_record: Dict) -> bool:
        """
        Check if an INSPIRE search result matches this entry

        Args:
            inspire_record: INSPIRE API record

        Returns:
            True if the record likely matches this entry
        """
        metadata = inspire_record.get("metadata", {})

        # Check DOI match (most reliable)
        if "doi" in self.fields:
            original_doi = self.fields["doi"].strip("{}").lower()
            inspire_dois = [
                doi.get("value", "").lower() for doi in metadata.get("dois", [])
            ]
            if original_doi and any(original_doi in doi for doi in inspire_dois):
                return True

        # Check arXiv/eprint match (very reliable)
        if "eprint" in self.fields:
            original_eprint = self.fields["eprint"].strip("{}").lower()
            inspire_eprints = [
                ep.get("value", "").lower() for ep in metadata.get("arxiv_eprints", [])
            ]
            if original_eprint and any(original_eprint in ep for ep in inspire_eprints):
                return True

        # Check title similarity (less reliable, so be more lenient)
        if "title" in self.fields:
            original_title = self.fields["title"].strip("{}").lower()
            inspire_titles = metadata.get("titles", [])
            for title_obj in inspire_titles:
                inspire_title = title_obj.get("title", "").lower()
                # Simple similarity check - check if titles have significant overlap
                if original_title and inspire_title:
                    # Remove common words and punctuation for better matching
                    import string

                    original_words = set(
                        word.strip(string.punctuation)
                        for word in original_title.split()
                        if len(word) > 2
                    )
                    inspire_words = set(
                        word.strip(string.punctuation)
                        for word in inspire_title.split()
                        if len(word) > 2
                    )
                    # Require at least 80% word overlap for title match (more lenient)
                    if len(original_words) > 0:
                        overlap = len(original_words & inspire_words) / len(
                            original_words
                        )
                        if overlap >= 0.8:
                            return True

        # If we can't verify the match, be conservative and reject it
        return False


class BibParser:
    """Parser for .bib files"""

    @staticmethod
    def parse_bib_file(filepath: str) -> List[BibEntry]:
        """
        Parse a .bib file and return list of entries

        Args:
            filepath: Path to .bib file

        Returns:
            List of BibEntry objects
        """
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        return BibParser.parse_bib_string(content)

    @staticmethod
    def parse_bib_string(content: str) -> List[BibEntry]:
        """
        Parse BibTeX string and return list of entries

        Args:
            content: BibTeX content as string

        Returns:
            List of BibEntry objects
        """
        entries = []

        # Regular expression to match BibTeX entries
        entry_pattern = r"@(\w+)\s*\{\s*([^,\s]+)\s*,\s*(.*?)\n\s*\}"

        for match in re.finditer(entry_pattern, content, re.DOTALL | re.IGNORECASE):
            entry_type = match.group(1).lower()
            key = match.group(2).strip()
            fields_text = match.group(3)

            # Parse fields
            fields = BibParser._parse_fields(fields_text)

            entries.append(BibEntry(entry_type, key, fields))

        return entries

    @staticmethod
    def _parse_fields(fields_text: str) -> Dict[str, str]:
        """Parse the fields section of a BibTeX entry"""
        fields = {}

        # More robust field parsing that handles nested braces and quotes
        field_pattern = (
            r'(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|"([^"]*)")\s*,?'
        )

        for match in re.finditer(field_pattern, fields_text, re.DOTALL):
            field_name = match.group(1).lower()
            # Use the brace-delimited value if available, otherwise quoted value
            field_value = (
                match.group(2) if match.group(2) is not None else match.group(3)
            )
            if field_value:
                fields[field_name] = field_value.strip()

        return fields


class BibSpire:
    """Main application class"""

    def __init__(self, delay: float = 1.0, verbose: bool = False):
        self.inspire = InspireAPI(delay)
        self.verbose = verbose

    def update_bib_file(
        self, input_file: str, output_file: Optional[str] = None
    ) -> None:
        """
        Update .bib file with INSPIRE entries

        Args:
            input_file: Path to input .bib file
            output_file: Path to output .bib file (defaults to input_file)
        """
        if output_file is None:
            output_file = input_file

        print(f"Reading {input_file}...")
        entries = BibParser.parse_bib_file(input_file)
        print(f"Found {len(entries)} entries")

        updated_entries = []

        for i, entry in enumerate(entries, 1):
            print(f"\nProcessing entry {i}/{len(entries)}: {entry.key}")

            # Generate search query
            query = entry.get_search_query()
            if not query:
                print(f"  Warning: Could not generate search query for {entry.key}")
                updated_entries.append(entry)
                continue

            if self.verbose:
                print(f"  Search query: {query}")

            # Search INSPIRE
            result = self.inspire.search_literature(query)

            if result is None:
                print(f"  No match found on INSPIRE for {entry.key}")
                updated_entries.append(entry)
                continue

            # Validate that the result actually matches our entry
            if not entry.matches_result(result):
                if self.verbose:
                    inspire_title = (
                        result.get("metadata", {})
                        .get("titles", [{}])[0]
                        .get("title", "Unknown")
                    )
                    print(
                        f"  Found '{inspire_title}' but it doesn't match {entry.key} - skipping"
                    )
                else:
                    print(f"  Found result but it doesn't match {entry.key} - skipping")
                updated_entries.append(entry)
                continue

            # Get record ID
            record_id = result["id"]
            print(f"  Found INSPIRE record: {record_id}")

            # Get BibTeX
            inspire_bibtex = self.inspire.get_bibtex(record_id)

            if inspire_bibtex is None:
                print(f"  Error getting BibTeX for {entry.key}")
                updated_entries.append(entry)
                continue

            # Parse INSPIRE BibTeX and update key
            inspire_entry = self._parse_inspire_bibtex(inspire_bibtex, entry.key)

            if inspire_entry:
                print("  Updated with INSPIRE data")
                updated_entries.append(inspire_entry)
            else:
                print(f"  Error parsing INSPIRE BibTeX for {entry.key}")
                updated_entries.append(entry)

        # Write updated file
        print(f"\nWriting updated bibliography to {output_file}...")
        self._write_bib_file(updated_entries, output_file)
        print("Done!")

    def _parse_inspire_bibtex(
        self, bibtex: str, original_key: str
    ) -> Optional[BibEntry]:
        """Parse INSPIRE BibTeX and replace key with original"""
        try:
            # Clean up the bibtex string
            bibtex = bibtex.strip()

            # Extract entry type, key, and fields
            match = re.match(
                r"@(\w+)\s*\{\s*([^,\s]+)\s*,\s*(.*?)\n\s*\}",
                bibtex,
                re.DOTALL | re.IGNORECASE,
            )

            if not match:
                return None

            entry_type = match.group(1).lower()
            fields_text = match.group(3)

            # Parse fields
            fields = BibParser._parse_fields(fields_text)

            # Create new entry with original key
            return BibEntry(entry_type, original_key, fields)

        except Exception as e:
            print(f"Error parsing INSPIRE BibTeX: {e}")
            return None

    def _write_bib_file(self, entries: List[BibEntry], filepath: str) -> None:
        """Write entries to .bib file"""
        with open(filepath, "w", encoding="utf-8") as f:
            for i, entry in enumerate(entries):
                if i > 0:
                    f.write("\n\n")
                f.write(entry.to_bibtex())
            f.write("\n")
