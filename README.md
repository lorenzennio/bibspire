# BibSpire

A Python tool to update .bib file entries with INSPIRE-HEP citations while preserving reference keys.

[![Tests](https://github.com/lorenzennio/bibspire/workflows/CI/badge.svg)](https://github.com/lorenzennio/bibspire/actions)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Coverage](https://img.shields.io/codecov/c/github/lorenzennio/bibspire)](https://codecov.io/gh/lorenzennio/bibspire)

## Overview

BibSpire reads a .bib file, searches each entry on inspire-hep.net, and replaces the entries with the official INSPIRE citations while keeping the same reference keys. This ensures your bibliography has the most accurate and complete citation information from INSPIRE-HEP.

## Features

- **Automatic INSPIRE Search**: Searches INSPIRE-HEP for each bibliography entry
- **Key Preservation**: Keeps original reference keys while updating content
- **Multiple Search Strategies**: Uses title, author, eprint, and DOI for matching
- **Robust Parsing**: Handles complex BibTeX formats with nested braces
- **Error Handling**: Gracefully handles missing entries and API errors
- **Rate Limiting**: Configurable delays between API requests
- **Code Quality**: Enforced with Ruff linting and formatting
- **Comprehensive Testing**: Full test suite with unit and integration tests

## Installation

### From PyPI (Recommended)

```bash
pip install bibspire
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/lorenzennio/bibspire.git
cd bibspire

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### From Built Package

```bash
# Build and install
python -m build
pip install dist/bibspire-1.0.0-py3-none-any.whl
```

## Usage

### Command Line Interface

```bash
# Basic usage - update file in place
bibspire input.bib

# Save to different file
bibspire input.bib -o output.bib

# Verbose output
bibspire input.bib -v

# Custom delay between API requests
bibspire input.bib -d 2.0

# Show help
bibspire --help
```

### Run as Python Module

```bash
python -m bibspire input.bib -o output.bib -v
```

### Programmatic Usage

```python
from bibspire import BibSpire, BibParser

# Create BibSpire instance
bibspire = BibSpire(delay=1.0, verbose=True)

# Update a bibliography file
bibspire.update_bib_file("input.bib", "output.bib")

# Or work with entries directly
entries = BibParser.parse_bib_file("input.bib")
updated_entries = bibspire.update_entries(entries)
```

## Testing

The project includes a comprehensive test suite:

```bash
# Run fast unit and integration tests
pytest tests/ -v -m "not slow"

# Run all tests including slow real API tests
pytest tests/ -v

# Run only slow tests (real API calls)
pytest tests/ -v -m "slow"

# Run tests with coverage
pytest tests/ --cov=bibspire --cov-report=html
```

### Test Categories

- **Unit Tests** (`test_core.py`, `test_cli.py`): Fast tests with mocked dependencies
- **Integration Tests** (`test_integration.py`): Tests with mocked HTTP responses
- **Slow Tests** (`test_slow.py`): Real API calls to INSPIRE-HEP (marked as `slow`)

## Development

### Building and Testing

```bash
# Use Makefile targets
make help                   # Show all available targets
make all                    # Install deps, install pre-commit, run checks, and build
make check                  # Run linting, formatting, and fast tests
make ci                     # Run full CI checks with coverage
make pre-commit-install     # Install pre-commit hooks
make pre-commit-run         # Run pre-commit on all files
make test                   # Run fast tests only
make test-cov               # Run fast tests with coverage
make lint                   # Run linting
make format                 # Format code

# Manual commands
pip install -e ".[dev]"    # Install with dev dependencies
pytest tests/ -v           # Run tests
pytest tests/ -v --cov=bibspire  # Run tests with coverage
ruff check src/ tests/     # Run linting
ruff format src/ tests/    # Format code
python -m build            # Build package
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks automatically run:
- Code linting and formatting with Ruff
- Trailing whitespace removal
- End-of-file fixes
- YAML and TOML validation
- Tests

To set up pre-commit hooks:

```bash
# Install and activate pre-commit hooks
make pre-commit-install

# Run pre-commit on all files manually
make pre-commit-run
```

Once installed, the hooks will run automatically on every commit. If any hook fails, the commit will be rejected until the issues are fixed.

### Publishing

#### Manual Publishing

```bash
# Install twine for uploading
pip install twine

# Check package integrity
twine check dist/*

# Upload to PyPI (requires account and authentication)
python -m twine upload dist/*
```

#### Automatic Publishing

The package is automatically published to PyPI when a new version tag is pushed:

```bash
git tag v1.0.1
git push origin v1.0.1
```

This triggers the release workflow which:
- Builds the package
- Checks package integrity
- Publishes to PyPI
- Creates a GitHub release

### Project Structure

```
bibspire/
├── .github/workflows/         # CI/CD workflows
├── src/bibspire/              # Main package
│   ├── __init__.py           # Package exports
│   ├── __main__.py           # Module entry point
│   ├── cli.py                # Command-line interface
│   └── core.py               # Core functionality
├── tests/                     # Test suite
│   ├── conftest.py           # Test fixtures
│   ├── test_core.py          # Core functionality tests
│   ├── test_cli.py           # CLI tests
│   ├── test_integration.py   # Integration tests
│   └── test_slow.py          # Slow API tests
├── pyproject.toml            # Package configuration
├── Makefile                  # Development commands
└── README.md                 # This file
```

## Example

Given an input .bib file:
```bibtex
@article{mykey2023,
  title = {Observation of a new particle in the search for the Standard Model Higgs boson},
  author = {Aad, G. and others},
  year = {2012}
}
```

BibSpire will search INSPIRE, find the official record, and replace it with:
```bibtex
@article{mykey2023,
  author = {Aad, Georges and others},
  collaboration = {ATLAS},
  title = {{Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC}},
  eprint = {1207.7214},
  archivePrefix = {arXiv},
  primaryClass = {hep-ex},
  doi = {10.1016/j.physletb.2012.08.020},
  journal = {Phys. Lett. B},
  volume = {716},
  pages = {1--29},
  year = {2012}
}
```

Note how the reference key `mykey2023` is preserved while all other fields are updated with official INSPIRE data.

## Dependencies

- Python ≥ 3.8
- requests ≥ 2.25.0

### Development Dependencies

- pytest ≥ 6.0.0
- pytest-mock ≥ 3.6.0
- responses ≥ 0.21.0
- ruff ≥ 0.1.0 (linting and formatting)
- build ≥ 0.8.0 (package building)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Run the test suite: `pytest tests/ -v`
5. Run linting: `make lint` or `ruff check src/ tests/`
6. Format code: `make format` or `ruff format src/ tests/`
7. Submit a pull request

### Code Quality

This project uses Ruff for linting and code formatting. The configuration includes:

- **Linting**: Enforces Python best practices, code style, and catches common errors
- **Formatting**: Consistent code style with 88-character line length
- **Import sorting**: Automatic import organization and cleanup
- **Type checking**: Basic type hint validation

Run `make check` to run all quality checks before submitting changes.

## Continuous Integration

This project uses GitHub Actions for automated testing and quality assurance:

### CI Workflow
- **Linting**: Ruff checks for code quality and style
- **Multi-Python Testing**: Tests run on Python 3.8-3.12
- **Coverage**: Code coverage reporting with Codecov integration
- **Integration Tests**: Slow tests run on main branch and when labeled
- **Package Building**: Validates package can be built locally

### Workflows
- `ci.yml`: Main CI pipeline for PRs and pushes
- `release.yml`: Automated publishing on version tags

### Quality Gates
All PRs must pass:
- Ruff linting (no violations)
- Code formatting check
- Test suite (35+ tests)
- Package build validation

To trigger slow integration tests, add the `run-slow-tests` label to your PR.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Troubleshooting

### Command Not Found

If `bibspire` command is not found:
```bash
# Use full path or activate virtual environment
/path/to/venv/bin/bibspire input.bib

# Or run as module
python -m bibspire input.bib
```

### API Rate Limiting

If you encounter rate limiting:
```bash
# Increase delay between requests
bibspire input.bib -d 2.0
```

### Test Failures

If tests fail:
```bash
# Check dependencies
pip install -e ".[test]"

# Run specific test
pytest tests/test_core.py::TestBibEntry::test_init -v
```
