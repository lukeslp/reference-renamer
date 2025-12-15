"""
Metadata enrichment module for Reference Renamer.
Handles extraction and enrichment of document metadata using multiple sources.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..api.semantic_scholar import SemanticScholarAPI
from ..api.arxiv import ArxivAPI
from ..api.ollama import OllamaAPI
from ..utils.exceptions import MetadataEnrichmentError
from ..utils.logging import get_logger


@dataclass
class ArticleMetadata:
    """Structured container for article metadata."""

    authors: List[str]
    year: Optional[int]
    title: str
    doi: Optional[str]
    abstract: Optional[str]
    keywords: List[str]
    source: Optional[str] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "authors": self.authors,
            "year": self.year,
            "title": self.title,
            "doi": self.doi,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "source": self.source,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArticleMetadata":
        """Create metadata from dictionary."""
        return cls(
            authors=data.get("authors", []),
            year=data.get("year"),
            title=data.get("title", ""),
            doi=data.get("doi"),
            abstract=data.get("abstract"),
            keywords=data.get("keywords", []),
            source=data.get("source"),
            confidence=data.get("confidence", 0.0),
        )


class MetadataEnricher:
    """Enriches document metadata using multiple sources."""

    def __init__(
        self,
        semantic_scholar_api: Optional[SemanticScholarAPI] = None,
        arxiv_api: Optional[ArxivAPI] = None,
        ollama_api: Optional[OllamaAPI] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the metadata enricher.

        Args:
            semantic_scholar_api: Optional Semantic Scholar API client
            arxiv_api: Optional arXiv API client
            ollama_api: Optional Ollama API client
            logger: Optional logger instance
        """
        self.semantic_scholar = semantic_scholar_api or SemanticScholarAPI()
        self.arxiv = arxiv_api or ArxivAPI()
        self.ollama = ollama_api or OllamaAPI()
        self.logger = logger or get_logger(__name__)

    async def enrich_metadata(
        self, initial_metadata: Dict[str, Any], content: str
    ) -> ArticleMetadata:
        """
        Enriches metadata using multiple sources.

        Args:
            initial_metadata: Initial metadata from file
            content: Document content

        Returns:
            Enriched ArticleMetadata

        Raises:
            MetadataEnrichmentError: If enrichment fails
        """
        try:
            # Extract basic metadata using LLM
            llm_metadata = await self._extract_with_llm(content)
            self.logger.info("Extracted initial metadata with LLM")

            # Search academic APIs
            arxiv_data = await self._search_arxiv(llm_metadata)
            scholar_data = await self._search_semantic_scholar(llm_metadata)

            # Combine all metadata sources
            combined = self._combine_metadata(
                initial_metadata, llm_metadata, arxiv_data, scholar_data
            )

            self.logger.info(f"Combined metadata from {combined.source}")
            return combined

        except Exception as e:
            raise MetadataEnrichmentError(f"Error enriching metadata: {str(e)}")

    async def _extract_with_llm(self, content: str) -> ArticleMetadata:
        """
        Extracts metadata from content using LLM.

        Args:
            content: Document content

        Returns:
            ArticleMetadata from LLM extraction
        """
        try:
            # Prepare content for LLM (truncate if needed)
            max_content_length = 2000
            truncated_content = content[:max_content_length]

            # Extract using Ollama
            result = await self.ollama.extract_metadata(truncated_content)

            if not result or not isinstance(result, dict):
                raise ValueError("Invalid LLM response")

            metadata = ArticleMetadata(
                authors=result.get("authors", []),
                year=self._parse_year(result.get("year")),
                title=result.get("title", ""),
                doi=result.get("doi"),
                abstract=result.get("abstract"),
                keywords=result.get("keywords", []),
                source="llm",
                confidence=0.7,
            )

            return metadata

        except Exception as e:
            self.logger.error(f"LLM extraction failed: {str(e)}")
            return ArticleMetadata(
                authors=[],
                year=None,
                title="",
                doi=None,
                abstract=None,
                keywords=[],
                source="llm_failed",
                confidence=0.0,
            )

    async def _search_arxiv(
        self, metadata: ArticleMetadata
    ) -> Optional[ArticleMetadata]:
        """
        Searches arXiv for matching paper.

        Args:
            metadata: Current metadata to use for search

        Returns:
            ArticleMetadata from arXiv or None if not found
        """
        try:
            # Construct search query
            query = f"ti:{metadata.title}"
            if metadata.authors:
                query += f" AND au:{metadata.authors[0]}"

            results = await self.arxiv.search_papers(query)
            if not results:
                return None

            # Get best match
            best_match = results[0]
            return ArticleMetadata(
                authors=best_match.get("authors", []),
                year=self._parse_year(best_match.get("year")),
                title=best_match.get("title", ""),
                doi=best_match.get("doi"),
                abstract=best_match.get("abstract"),
                keywords=best_match.get("keywords", []),
                source="arxiv",
                confidence=0.9,
            )

        except Exception as e:
            self.logger.error(f"arXiv search failed: {str(e)}")
            return None

    async def _search_semantic_scholar(
        self, metadata: ArticleMetadata
    ) -> Optional[ArticleMetadata]:
        """
        Searches Semantic Scholar for matching paper.

        Args:
            metadata: Current metadata to use for search

        Returns:
            ArticleMetadata from Semantic Scholar or None if not found
        """
        try:
            # Search by DOI if available
            if metadata.doi:
                result = await self.semantic_scholar.get_paper_by_doi(metadata.doi)
                if result:
                    return self._parse_semantic_scholar_result(result)

            # Search by title
            results = await self.semantic_scholar.search_paper(metadata.title)
            if not results:
                return None

            # Get best match
            best_match = results[0]
            return self._parse_semantic_scholar_result(best_match)

        except Exception as e:
            self.logger.error(f"Semantic Scholar search failed: {str(e)}")
            return None

    def _combine_metadata(
        self,
        initial: Dict[str, Any],
        llm: ArticleMetadata,
        arxiv: Optional[ArticleMetadata],
        scholar: Optional[ArticleMetadata],
    ) -> ArticleMetadata:
        """
        Combines metadata from multiple sources.

        Args:
            initial: Initial metadata from file
            llm: Metadata from LLM
            arxiv: Metadata from arXiv
            scholar: Metadata from Semantic Scholar

        Returns:
            Combined ArticleMetadata
        """
        # Start with highest confidence source
        sources = [(scholar, 0.9), (arxiv, 0.8), (llm, 0.7)]

        base = None
        confidence = 0.0

        for source, conf in sources:
            if source and source.title:
                base = source
                confidence = conf
                break

        if not base:
            # Fall back to LLM results
            return llm

        # Enhance with other sources
        base.confidence = confidence

        # Add any missing information from other sources
        for source, _ in sources:
            if not source or source == base:
                continue

            if not base.doi and source.doi:
                base.doi = source.doi
            if not base.abstract and source.abstract:
                base.abstract = source.abstract
            if not base.year and source.year:
                base.year = source.year

            # Combine keywords
            base.keywords = list(set(base.keywords + source.keywords))

        return base

    def _parse_year(self, year_str: Optional[str]) -> Optional[int]:
        """Parses year from string."""
        if not year_str:
            return None

        try:
            # Try direct conversion
            year = int(year_str)
            if 1900 <= year <= datetime.now().year:
                return year

            # Try extracting from date string
            from dateutil import parser

            date = parser.parse(year_str)
            return date.year

        except Exception:
            return None

    def _parse_semantic_scholar_result(self, result: Dict[str, Any]) -> ArticleMetadata:
        """Parses Semantic Scholar API result."""
        return ArticleMetadata(
            authors=[a.get("name", "") for a in result.get("authors", [])],
            year=self._parse_year(result.get("year")),
            title=result.get("title", ""),
            doi=result.get("doi"),
            abstract=result.get("abstract"),
            keywords=result.get("keywords", []),
            source="semantic_scholar",
            confidence=0.9,
        )
