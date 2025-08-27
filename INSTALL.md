# BibSpire Installation and Usage Guide

## Package Structure

```
bibspire/
├── src/
│   └── bibspire/
│       ├── __init__.py       # Package initialization
│       ├── __main__.py       # Module entry point
│       ├── cli.py           # Command-line interface
│       └── core.py          # Core functionality
├── pyproject.toml           # Package configuration
├── LICENSE                 # MIT License
├── README.md              # Main documentation
└── Makefile               # Development commands

```

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install bibspire
```

### Option 2: Development Installation (For contributors)

```bash
# Clone or navigate to the project directory
cd /path/to/bibspire

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Option 3: Install from Built Package

```bash
# Build the package
python -m build

# Install from wheel
pip install dist/bibspire-1.0.0-py3-none-any.whl
```

## Usage

### Command Line Interface

After installation, you can use the `bibspire` command:

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

# Show version
bibspire --version
```

### Run as Python Module

You can also run BibSpire as a Python module:

```bash
# Same functionality as CLI
python -m bibspire input.bib -o output.bib -v

# Show version
python -m bibspire --version
```

### Programmatic Usage

You can also use BibSpire in your Python code:

```python
from bibspire import BibSpire, BibParser

# Create BibSpire instance
bibspire = BibSpire(delay=1.0, verbose=True)

# Update a bibliography file
bibspire.update_bib_file("input.bib", "output.bib")

# Or parse and work with entries directly
entries = BibParser.parse_bib_file("input.bib")
for entry in entries:
    print(f"Entry: {entry.key}")
    print(f"Title: {entry.fields.get('title', 'N/A')}")
```

## Building and Distribution

### Build Package

```bash
# Install build dependencies
pip install build

# Build the package
python -m build

# This creates:
# - dist/bibspire-1.0.0.tar.gz (source distribution)
# - dist/bibspire-1.0.0-py3-none-any.whl (wheel)
```

### Upload to PyPI

```bash
# Install twine for uploading
pip install twine

# Check package integrity
twine check dist/*

# Upload to PyPI (requires account and authentication)
python -m twine upload dist/*
```

### Automatic Publishing

The package is automatically published to PyPI when a new version tag is pushed:

```bash
git tag v*.*.*
git push origin v*.*.*
```

This triggers the release workflow which:
- Builds the package
- Checks package integrity
- Publishes to PyPI
- Creates a GitHub release

## Features

- **Automatic INSPIRE Search**: Searches INSPIRE-HEP for each bibliography entry
- **Key Preservation**: Keeps original reference keys while updating content
- **Multiple Search Strategies**: Uses title, author, eprint, and DOI for matching
- **Robust Parsing**: Handles complex BibTeX formats with nested braces
- **Error Handling**: Gracefully handles missing entries and API errors
- **Rate Limiting**: Configurable delays between API requests
- **Verbose Output**: Optional detailed progress information

## Configuration

The tool can be configured through command-line arguments:

- `--delay`: Set delay between API requests (default: 1.0 seconds)
- `--verbose`: Enable detailed output
- `--output`: Specify output file (default: overwrites input)

## Dependencies

- Python ≥ 3.8
- requests ≥ 2.25.0

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Package Import Issues

If you have issues importing the package, make sure:
1. The old `bibspire.py` file is not in your current directory
2. The package is properly installed (`pip list | grep bibspire`)
3. You're using the correct Python environment

### Command Not Found

If `bibspire` command is not found:
1. Make sure the package is installed in the current environment
2. Use the full path: `/path/to/venv/bin/bibspire`
3. Or run as module: `python -m bibspire`

### API Rate Limiting

If you encounter rate limiting issues:
1. Increase the delay: `bibspire input.bib -d 2.0`
2. Process smaller batches of entries
3. Check INSPIRE-HEP status if persistent issues occur
