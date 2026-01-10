# citewalker

Anybody else have a huge folder full of files with names like `235680_download.PDF` and `smith_et_al_2008_full.pdf(2)`?

... yeah.

This a Python command line tool that:

- Strips text from files and uses arXiv, semantic scholar, and a couple of free "why not" APIs to find full source
- Renames academic articles to a standardized format (`Author_Year_FiveWordTitle.ext`).
- Handles PDF (obvs) and most other document formats. Throw it at it, let's find out.
- Maintains a BibTeX database of all processed articles.
- Logs everything, doesn't break anything, asks for approval.
- OPTIONALLY: Uses a small local language model to help if that still fails.

## Installation

For PDF processing with OCR, you will need to install Tesseract and Poppler; if you primarily use PDFs or other files with actual text (meaning not scans of PDFs or those weird ones you can't select), then you don't need this part.

### Python Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/lukeslp/citewalker.git
   cd citewalker
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Ollama (Optional)

If traditional methods fail, it can use a language model to generate adjacent search terms. This can help with corrupted files or partial sources. This is an optional feature; the tool will function; just an added additional layer.

If you wish to use Ollama:

1. Install Ollama from [https://ollama.ai](https://ollama.ai).
2. Run a model, for example: `ollama run drummer-knowledge`

## Usage

### Basic Usage

```bash
# Process a single directory
citewalker /path/to/your/papers

# Process a directory recursively with a dry run (no actual renaming)
citewalker --recursive --dry-run /path/to/your/papers

# Generate citations without renaming files
citewalker --citations-only /path/to/your/papers
```

### Configuration

In `config.yaml` file in your working directory:

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

## License

The MIT "do whatever you want" license. See [LICENSE](LICENSE) for details.
