# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-minimal.txt  # Core dependencies only (recommended)
# OR
pip install -r requirements.txt  # Full dependencies (400+ packages)

# Install package in development mode
pip install -e .
```

### Code Quality
```bash
# Code formatting
black .

# Import sorting
isort .

# Type checking
mypy .

# Linting (if configured)
flake8
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=reference_renamer

# Run specific test file
pytest tests/test_file_processor.py
```

### CLI Usage
The tool has three entry points (all aliases):
```bash
reference-renamer [OPTIONS] [DIRECTORY]
reref [OPTIONS] [DIRECTORY]
schollama [OPTIONS] [DIRECTORY]

# Common options:
--recursive         # Process subdirectories
--dry-run          # Preview changes without applying
--citations-only   # Generate citations without renaming
--verbose          # Detailed output
```

## Architecture Overview

This is an academic reference management CLI tool that standardizes filenames using AI-powered metadata extraction.

### Core Modules

**`reference_renamer/cli/`**: Command-line interface using Click
- `main.py` - Entry point with command definitions

**`reference_renamer/core/`**: Core processing logic
- `file_processor.py` - File discovery and validation
- `content_extractor.py` - PDF/text content extraction with OCR fallback
- `metadata_enricher.py` - Metadata extraction via LLM and APIs
- `filename_generator.py` - Standardized filename creation (`Author_Year_FiveWordTitle.ext`)
- `change_logger.py` - CSV logging and operation tracking

**`reference_renamer/api/`**: External integrations
- `ollama.py` - Local LLM integration (requires `drummer-knowledge` model)
- `arxiv.py` - arXiv API for academic metadata
- `semantic_scholar.py` - Semantic Scholar API integration

**`reference_renamer/utils/`**: Utilities
- `logging.py` - Accessibility-focused logging with structlog
- `exceptions.py` - Custom exception classes
- `citations.py` - BibTeX generation and management

### Key Design Patterns

1. **Async Processing**: Uses asyncio for concurrent API calls to academic services
2. **Graceful Degradation**: Falls back through multiple metadata sources (LLM → arXiv → Semantic Scholar)
3. **Accessibility First**: Screen reader support, high contrast output, structured logging
4. **Comprehensive Logging**: Maintains CSV logs and BibTeX citation database

### Configuration

The tool supports YAML configuration files:
```yaml
processing:
  supported_extensions: [.pdf, .txt]
  recursive: true
  max_title_words: 5

apis:
  semantic_scholar:
    enabled: true
    timeout: 30
  arxiv:
    enabled: true
    max_results: 3
```

### Output Files

- `rename_log.csv` - Detailed operation log
- `citations.bib` - BibTeX database of processed articles
- Original files are backed up before renaming

## Important Notes

- **Ollama Dependency**: Requires Ollama running with `drummer-knowledge` model
- **No Test Suite**: Tests are configured but not yet implemented
- **Python 3.8+**: Minimum Python version requirement
- **Academic Focus**: Specifically designed for academic papers with standardized naming