"""
Fixtures and test data for BibSpire tests
"""

import pytest

from bibspire.core import BibEntry


@pytest.fixture
def sample_bib_entry():
    """Sample bibliography entry for testing"""
    return BibEntry(
        entry_type="article",
        key="test2023",
        fields={
            "title": "A Test Paper Title",
            "author": "Smith, John and Doe, Jane",
            "year": "2023",
            "journal": "Test Journal",
        },
    )


@pytest.fixture
def sample_higgs_entry():
    """Real Higgs discovery paper entry"""
    return BibEntry(
        entry_type="article",
        key="higgs2012",
        fields={
            "title": "Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC",
            "author": "Aad, G. and others",
            "year": "2012",
        },
    )


@pytest.fixture
def sample_bib_content():
    """Sample BibTeX file content"""
    return """@article{test2023,
  title = {A Test Paper Title},
  author = {Smith, John and Doe, Jane},
  year = {2023},
  journal = {Test Journal}
}

@article{higgs2012,
  title = {Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC},
  author = {Aad, G. and others},
  year = {2012}
}"""


@pytest.fixture
def invalid_bib_content():
    """Invalid BibTeX content for error testing"""
    return """@article{incomplete,
  title = Missing closing brace
  author = "No equals sign"
}"""


@pytest.fixture
def mock_inspire_response():
    """Mock INSPIRE API response"""
    return {
        "hits": {
            "total": 1,
            "hits": [
                {
                    "id": "1124337",
                    "metadata": {
                        "titles": [{"title": "Observation of a new particle..."}],
                        "authors": [{"full_name": "Aad, G."}],
                    },
                }
            ],
        }
    }


@pytest.fixture
def mock_inspire_bibtex():
    """Mock INSPIRE BibTeX response"""
    return """@article{Aad:2012tfa,
    author = "Aad, Georges and others",
    collaboration = "ATLAS",
    title = "{Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC}",
    eprint = "1207.7214",
    archivePrefix = "arXiv",
    primaryClass = "hep-ex",
    reportNumber = "CERN-PH-EP-2012-218",
    doi = "10.1016/j.physletb.2012.08.020",
    journal = "Phys. Lett. B",
    volume = "716",
    pages = "1--29",
    year = "2012"
}"""


@pytest.fixture
def temp_bib_file(tmp_path, sample_bib_content):
    """Create a temporary BibTeX file"""
    bib_file = tmp_path / "test.bib"
    bib_file.write_text(sample_bib_content)
    return str(bib_file)
