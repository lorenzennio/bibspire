"""
Slow integration tests that make real API calls to INSPIRE-HEP
These tests are marked as 'slow' and should only be run when needed
"""

import time

import pytest

from bibspire.core import BibParser, BibSpire, InspireAPI


@pytest.mark.slow
class TestRealAPI:
    """Tests that make real API calls - marked as slow"""

    def test_real_higgs_search(self):
        """Test searching for real Higgs discovery paper"""
        api = InspireAPI(delay=1.0)

        # Search for the ATLAS Higgs discovery paper
        query = 'title:"Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC"'
        result = api.search_literature(query)

        assert result is not None
        assert "id" in result

        # Get BibTeX for the found record
        bibtex = api.get_bibtex(result["id"])
        assert bibtex is not None
        assert "@" in bibtex
        assert "Higgs" in bibtex or "higgs" in bibtex.lower()

    def test_real_nonexistent_paper(self):
        """Test searching for a paper that doesn't exist"""
        api = InspireAPI(delay=1.0)

        # Search for a clearly fake paper
        query = 'title:"This Paper Definitely Does Not Exist In INSPIRE Database 12345"'
        result = api.search_literature(query)

        assert result is None

    def test_real_end_to_end(self, tmp_path):
        """Test complete workflow with real API"""
        # Create a test file with a real paper
        test_content = """@article{higgs_test,
  title = {Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC},
  author = {Aad, G. and others},
  year = {2012}
}"""

        input_file = tmp_path / "real_test.bib"
        output_file = tmp_path / "real_output.bib"

        input_file.write_text(test_content)

        # Run BibSpire with real API
        bibspire = BibSpire(delay=1.0, verbose=True)
        bibspire.update_bib_file(str(input_file), str(output_file))

        # Verify the output
        assert output_file.exists()

        # Parse the result
        updated_entries = BibParser.parse_bib_file(str(output_file))
        assert len(updated_entries) == 1

        entry = updated_entries[0]
        assert entry.key == "higgs_test"  # Key should be preserved

        # Should have more complete information now
        assert "doi" in entry.fields or "eprint" in entry.fields
        assert "journal" in entry.fields or "Phys" in entry.fields.get("journal", "")


@pytest.mark.slow
def test_api_rate_limiting():
    """Test that API rate limiting works properly"""
    api = InspireAPI(delay=0.5)

    start_time = time.time()

    # Make two API calls
    api.search_literature('title:"test"')
    api.search_literature('title:"test2"')

    elapsed = time.time() - start_time

    # Should take at least 0.5 seconds due to rate limiting
    assert elapsed >= 0.5
