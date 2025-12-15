# Reference Renamer

A powerful CLI tool for standardizing academic article filenames using intelligent metadata extraction and verification.

## Features

- **Intelligent Renaming**: Automatically renames academic articles to a standardized format (`Author_Year_FiveWordTitle.ext`)
- **Multiple Format Support**: Handles PDF, TXT, and other document formats
- **Metadata Enrichment**: Uses arXiv, Semantic Scholar, and LLM processing to verify and enrich document metadata
- **Citation Management**: Maintains a BibTeX database of processed articles
- **Accessibility Focused**: Clear output formats and screen reader support
- **Comprehensive Logging**: Detailed tracking of all file operations

## Installation

### System Dependencies

**Required for PDF processing with OCR:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler

# Windows
# Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
```

**Note:** OCR is only used as a fallback when PDFs contain no extractable text. If you only process text-based PDFs, these dependencies are optional.

### Python Installation

1. Clone the repository:
```bash
git clone https://github.com/lukeslp/reference-renamer.git
cd reference-renamer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Ollama (Optional)

Ollama provides local LLM processing for enhanced metadata extraction. **It is optional** - the tool works without it using arXiv and Semantic Scholar APIs.

If you want to use Ollama:
```bash
# Install Ollama from https://ollama.ai
ollama run drummer-knowledge
```

Without Ollama, the tool will:
- Skip LLM-based extraction
- Fall back to arXiv and Semantic Scholar for metadata
- Still function correctly for most academic papers

## Usage

### Basic Usage

```bash
# Process a single directory
reference-renamer /path/to/papers

# Process recursively with dry run
reference-renamer --recursive --dry-run /path/to/papers

# Generate citations only
reference-renamer --citations-only /path/to/papers
```

### Configuration

Create a `config.yaml` file in your working directory:

```yaml
processing:
  supported_extensions:
    - .pdf
    - .txt
  recursive: true
  max_title_words: 5

apis:
  semantic_scholar:
    enabled: true
    timeout: 30
  arxiv:
    enabled: true
    max_results: 3

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Output

The tool generates:
1. Renamed files in the specified format
2. A CSV log of all operations (`rename_log.csv`)
3. A BibTeX database of citations (`citations.bib`)

## Accessibility Features

- Screen reader-friendly output formats
- High contrast CLI interface
- Clear error messages and status updates
- Configurable output formats

## Development

### Setting up the Development Environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=reference_renamer

# Run specific test file
pytest tests/test_file_processor.py
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run the full suite:
```bash
# Format code
black .
isort .

# Check types
mypy .

# Lint
flake8
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

Please ensure your PR:
- Includes tests for new features
- Updates documentation as needed
- Follows the project's code style
- Includes a clear description of changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Python](https://python.org)
- Uses [Ollama](https://ollama.ai) for LLM processing
- Integrates with [arXiv](https://arxiv.org) and [Semantic Scholar](https://semanticscholar.org)

## Support

For support, please:
1. Check the documentation in this README
2. Search [existing issues](https://github.com/lukeslp/reference-renamer/issues)
3. Create a new issue if needed 
## What's New
This refactor archives old helpers, adds example snippets, and includes new funding links.

## Credits & Support
- [Tip Jar](https://usefulai.lemonsqueezy.com/buy/bf6ce1bd-85f5-4a09-ba10-191a670f74af)
- [Substack](https://assisted.site/)
- [GitHub](https://github.com/lukeslp)
- [Bluesky](https://bsky.app/profile/lukeslp.bsky.social)
- [LinkedIn](https://www.linkedin.com/in/lukesteuber)
