"""
Unit tests for BibSpire core functionality
"""

from unittest.mock import mock_open, patch

from bibspire.core import BibEntry, BibParser, BibSpire, InspireAPI


class TestBibEntry:
    """Test BibEntry class"""

    def test_init(self, sample_bib_entry):
        """Test BibEntry initialization"""
        assert sample_bib_entry.entry_type == "article"
        assert sample_bib_entry.key == "test2023"
        assert sample_bib_entry.fields["title"] == "A Test Paper Title"
        assert sample_bib_entry.fields["author"] == "Smith, John and Doe, Jane"

    def test_to_bibtex(self, sample_bib_entry):
        """Test BibTeX output generation"""
        bibtex = sample_bib_entry.to_bibtex()

        assert bibtex.startswith("@article{test2023,")
        assert "title = {A Test Paper Title}," in bibtex
        assert "author = {Smith, John and Doe, Jane}," in bibtex
        assert bibtex.endswith("}")

    def test_get_search_query_with_title(self, sample_bib_entry):
        """Test search query generation with title"""
        query = sample_bib_entry.get_search_query()
        assert query == 'title:"A Test Paper Title"'

    def test_get_search_query_with_eprint(self):
        """Test search query generation with eprint"""
        entry = BibEntry("article", "test", {"eprint": "2301.12345"})
        query = entry.get_search_query()
        assert query == "eprint:2301.12345"

    def test_get_search_query_with_doi(self):
        """Test search query generation with DOI"""
        entry = BibEntry("article", "test", {"doi": "10.1103/PhysRevD.108.123456"})
        query = entry.get_search_query()
        assert query == "doi:10.1103/PhysRevD.108.123456"

    def test_get_search_query_empty(self):
        """Test search query generation with no useful fields"""
        entry = BibEntry("article", "test", {"year": "2023"})
        query = entry.get_search_query()
        assert query == ""


class TestBibParser:
    """Test BibParser class"""

    def test_parse_bib_string(self, sample_bib_content):
        """Test parsing BibTeX string"""
        entries = BibParser.parse_bib_string(sample_bib_content)

        assert len(entries) == 2
        assert entries[0].key == "test2023"
        assert entries[1].key == "higgs2012"
        assert entries[0].entry_type == "article"
        assert entries[0].fields["title"] == "A Test Paper Title"

    @patch("builtins.open", new_callable=mock_open)
    def test_parse_bib_file(self, mock_file, sample_bib_content):
        """Test parsing BibTeX file"""
        mock_file.return_value.read.return_value = sample_bib_content

        entries = BibParser.parse_bib_file("test.bib")

        mock_file.assert_called_once_with("test.bib", encoding="utf-8")
        assert len(entries) == 2

    def test_parse_fields_with_braces(self):
        """Test field parsing with braces"""
        fields_text = "title = {A {Complex} Title}, author = {Smith, J.}"
        fields = BibParser._parse_fields(fields_text)

        assert fields["title"] == "A {Complex} Title"
        assert fields["author"] == "Smith, J."

    def test_parse_fields_with_quotes(self):
        """Test field parsing with quotes"""
        fields_text = 'title = "A Simple Title", year = "2023"'
        fields = BibParser._parse_fields(fields_text)

        assert fields["title"] == "A Simple Title"
        assert fields["year"] == "2023"

    def test_parse_empty_content(self):
        """Test parsing empty content"""
        entries = BibParser.parse_bib_string("")
        assert len(entries) == 0

    def test_parse_malformed_entry(self):
        """Test parsing malformed entry"""
        malformed = "@article{test\n  title = incomplete"
        entries = BibParser.parse_bib_string(malformed)
        assert len(entries) == 0


class TestInspireAPI:
    """Test InspireAPI class"""

    def test_init(self):
        """Test InspireAPI initialization"""
        api = InspireAPI(delay=2.0)
        assert api.delay == 2.0
        assert api.BASE_URL == "https://inspirehep.net/api"
        assert "BibSpire" in api.session.headers["User-Agent"]

    @patch("requests.Session.get")
    @patch("time.sleep")
    def test_search_literature_success(
        self, mock_sleep, mock_get, mock_inspire_response
    ):
        """Test successful literature search"""
        mock_get.return_value.json.return_value = mock_inspire_response
        mock_get.return_value.raise_for_status.return_value = None

        api = InspireAPI(delay=0.1)
        result = api.search_literature('title:"Test Title"')

        assert result is not None
        assert result["id"] == "1124337"
        mock_sleep.assert_called_once_with(0.1)

    @patch("requests.Session.get")
    @patch("time.sleep")
    def test_search_literature_no_results(self, mock_sleep, mock_get):
        """Test literature search with no results"""
        mock_get.return_value.json.return_value = {"hits": {"total": 0, "hits": []}}
        mock_get.return_value.raise_for_status.return_value = None

        api = InspireAPI(delay=0.1)
        result = api.search_literature('title:"Nonexistent Paper"')

        assert result is None
        mock_sleep.assert_called_once_with(0.1)

    @patch("requests.Session.get")
    @patch("time.sleep")
    def test_search_literature_error(self, mock_sleep, mock_get):
        """Test literature search with error"""
        mock_get.side_effect = Exception("Network error")

        api = InspireAPI(delay=0.1)
        result = api.search_literature('title:"Test"')

        assert result is None
        mock_sleep.assert_called_once_with(0.1)

    @patch("requests.Session.get")
    @patch("time.sleep")
    def test_get_bibtex_success(self, mock_sleep, mock_get, mock_inspire_bibtex):
        """Test successful BibTeX retrieval"""
        mock_get.return_value.text = mock_inspire_bibtex
        mock_get.return_value.raise_for_status.return_value = None

        api = InspireAPI(delay=0.1)
        result = api.get_bibtex("1124337")

        assert result == mock_inspire_bibtex
        mock_sleep.assert_called_once_with(0.1)

    @patch("requests.Session.get")
    @patch("time.sleep")
    def test_get_bibtex_error(self, mock_sleep, mock_get):
        """Test BibTeX retrieval with error"""
        mock_get.side_effect = Exception("Network error")

        api = InspireAPI(delay=0.1)
        result = api.get_bibtex("1124337")

        assert result is None
        mock_sleep.assert_called_once_with(0.1)


class TestBibSpire:
    """Test BibSpire main class"""

    def test_init(self):
        """Test BibSpire initialization"""
        bibspire = BibSpire(delay=2.0, verbose=True)
        assert bibspire.inspire.delay == 2.0
        assert bibspire.verbose is True

    @patch("bibspire.core.BibParser.parse_bib_file")
    def test_update_bib_file(self, mock_parse, sample_bib_entry):
        """Test updating BibTeX file"""
        mock_parse.return_value = [sample_bib_entry]

        bibspire = BibSpire(delay=0.1, verbose=False)
        with patch.object(bibspire, "_write_bib_file") as mock_write, patch.object(
            bibspire.inspire, "search_literature", return_value=None
        ):
            bibspire.update_bib_file("test.bib", "output.bib")

        mock_parse.assert_called_once_with("test.bib")
        mock_write.assert_called_once()

    def test_parse_inspire_bibtex(self, mock_inspire_bibtex):
        """Test parsing INSPIRE BibTeX"""
        bibspire = BibSpire()
        entry = bibspire._parse_inspire_bibtex(mock_inspire_bibtex, "original_key")

        assert entry is not None
        assert entry.key == "original_key"  # Key should be preserved
        assert entry.entry_type == "article"
        assert "Georges" in entry.fields["author"]

    def test_parse_inspire_bibtex_invalid(self):
        """Test parsing invalid INSPIRE BibTeX"""
        bibspire = BibSpire()
        entry = bibspire._parse_inspire_bibtex("invalid bibtex", "key")

        assert entry is None

    @patch("builtins.open", new_callable=mock_open)
    def test_write_bib_file(self, mock_file, sample_bib_entry):
        """Test writing BibTeX file"""
        bibspire = BibSpire()
        entries = [sample_bib_entry]

        bibspire._write_bib_file(entries, "output.bib")

        mock_file.assert_called_once_with("output.bib", "w", encoding="utf-8")
        written_content = "".join(
            call.args[0] for call in mock_file().write.call_args_list
        )
        assert "@article{test2023," in written_content
        assert "title = {A Test Paper Title}," in written_content
