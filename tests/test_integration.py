"""
Integration tests for BibSpire using mocked HTTP responses
"""

from pathlib import Path

import responses

from bibspire.core import BibParser, BibSpire


class TestIntegration:
    """Integration tests with mocked API responses"""

    @responses.activate
    def test_end_to_end_with_mock_api(
        self, temp_bib_file, mock_inspire_response, mock_inspire_bibtex
    ):
        """Test complete workflow with mocked INSPIRE API"""
        # Mock the search API
        responses.add(
            responses.GET,
            "https://inspirehep.net/api/literature",
            json=mock_inspire_response,
            status=200,
        )

        # Mock the BibTeX API
        responses.add(
            responses.GET,
            "https://inspirehep.net/api/literature/1124337",
            body=mock_inspire_bibtex,
            status=200,
        )

        # Create output file path
        output_file = str(Path(temp_bib_file).parent / "output.bib")

        # Run BibSpire
        bibspire = BibSpire(delay=0.1, verbose=False)
        bibspire.update_bib_file(temp_bib_file, output_file)

        # Verify output file was created
        assert Path(output_file).exists()

        # Parse and verify the output
        updated_entries = BibParser.parse_bib_file(output_file)
        assert len(updated_entries) == 2

        # Check that the first entry (which should match) was updated
        higgs_entry = next(e for e in updated_entries if e.key == "higgs2012")
        assert higgs_entry.key == "higgs2012"  # Key preserved
        assert "Georges" in higgs_entry.fields.get("author", "")  # Content updated
        assert higgs_entry.fields.get("doi") == "10.1016/j.physletb.2012.08.020"

    @responses.activate
    def test_no_match_found(self, temp_bib_file):
        """Test behavior when no INSPIRE match is found"""
        # Mock API to return no results
        responses.add(
            responses.GET,
            "https://inspirehep.net/api/literature",
            json={"hits": {"total": 0, "hits": []}},
            status=200,
        )

        output_file = str(Path(temp_bib_file).parent / "no_match_output.bib")

        bibspire = BibSpire(delay=0.1, verbose=False)
        bibspire.update_bib_file(temp_bib_file, output_file)

        # Verify original entries are preserved when no match found
        original_entries = BibParser.parse_bib_file(temp_bib_file)
        updated_entries = BibParser.parse_bib_file(output_file)

        assert len(original_entries) == len(updated_entries)
        for orig, upd in zip(original_entries, updated_entries):
            assert orig.key == upd.key
            assert orig.fields == upd.fields

    @responses.activate
    def test_api_error_handling(self, temp_bib_file):
        """Test behavior when API returns errors"""
        # Mock API to return 500 error
        responses.add(
            responses.GET,
            "https://inspirehep.net/api/literature",
            json={"error": "Internal server error"},
            status=500,
        )

        output_file = str(Path(temp_bib_file).parent / "error_output.bib")

        bibspire = BibSpire(delay=0.1, verbose=False)
        bibspire.update_bib_file(temp_bib_file, output_file)

        # Verify original entries are preserved when API errors occur
        original_entries = BibParser.parse_bib_file(temp_bib_file)
        updated_entries = BibParser.parse_bib_file(output_file)

        assert len(original_entries) == len(updated_entries)

    def test_file_operations(self, tmp_path, sample_bib_content):
        """Test file reading and writing operations"""
        input_file = tmp_path / "input.bib"
        output_file = tmp_path / "output.bib"

        # Create input file
        input_file.write_text(sample_bib_content)

        # Parse entries
        entries = BibParser.parse_bib_file(str(input_file))
        assert len(entries) == 2

        # Test writing
        bibspire = BibSpire()
        bibspire._write_bib_file(entries, str(output_file))

        # Verify output file
        assert output_file.exists()
        output_content = output_file.read_text()
        assert "@article{test2023," in output_content
        assert "@article{higgs2012," in output_content

    def test_malformed_bib_file(self, tmp_path):
        """Test handling of malformed BibTeX files"""
        malformed_content = """@article{incomplete
  title = {Missing closing brace
  author = No quotes or braces
"""

        input_file = tmp_path / "malformed.bib"
        input_file.write_text(malformed_content)

        # Should not crash, but return empty list
        entries = BibParser.parse_bib_file(str(input_file))
        assert len(entries) == 0
