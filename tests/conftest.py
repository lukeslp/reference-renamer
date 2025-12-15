"""Pytest configuration and fixtures for reference-renamer tests."""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a sample PDF file path for testing."""
    pdf_path = temp_dir / "sample.pdf"
    pdf_path.touch()  # Create empty file for path testing
    return pdf_path


@pytest.fixture
def sample_text_content():
    """Sample academic text content for testing."""
    return """
    This is a sample academic paper about quantum computing.
    The research was conducted at MIT in 2023.
    Authors: John Doe, Jane Smith
    DOI: 10.1234/sample.2023
    """


@pytest.fixture
def mock_arxiv_result():
    """Mock ArXiv API result."""
    return {
        'title': 'Quantum Computing Applications in Machine Learning',
        'authors': ['John Doe', 'Jane Smith'],
        'published': '2023-05-15',
        'doi': '10.1234/arxiv.2023.12345'
    }


@pytest.fixture
def sample_filename():
    """Sample generated filename for testing."""
    return "JohnDoe_2023_Quantum_Computing_Applications_ML.pdf"

