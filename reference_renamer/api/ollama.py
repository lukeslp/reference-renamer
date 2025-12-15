"""
Ollama API integration module for Reference Renamer.
Handles interaction with Ollama LLM service for metadata extraction.
"""

import logging
from typing import Dict, Any, Optional, List
import json

import aiohttp
import backoff

from ..utils.exceptions import APIError
from ..utils.logging import get_logger


class OllamaAPI:
    """Client for interacting with Ollama LLM service."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434/api",
        model: str = "drummer-knowledge",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Ollama API client.

        Args:
            base_url: Base URL for Ollama API
            model: Model to use for inference
            logger: Optional logger instance
        """
        self.base_url = base_url
        self.model = model
        self.logger = logger or get_logger(__name__)
        self._available: Optional[bool] = None

    async def is_available(self) -> bool:
        """
        Check if Ollama service is available.

        Returns:
            True if Ollama is running and accessible
        """
        if self._available is not None:
            return self._available

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url.replace('/api', '')}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    self._available = response.status == 200
                    if self._available:
                        self.logger.debug("Ollama service is available")
                    return self._available
        except Exception:
            self._available = False
            self.logger.info("Ollama service not available - will use API fallbacks")
            return False

    @backoff.on_exception(
        backoff.expo, (aiohttp.ClientError, TimeoutError), max_tries=3
    )
    async def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from document content using LLM.

        Args:
            content: Document content to analyze

        Returns:
            Extracted metadata

        Raises:
            APIError: If API request fails or Ollama unavailable
        """
        # Check availability first to fail fast
        if not await self.is_available():
            raise APIError("Ollama service not available", "Ollama")

        try:
            prompt = self._construct_metadata_prompt(content)
            response = await self._call_ollama(prompt)
            return self._parse_metadata_response(response)

        except Exception as e:
            raise APIError(f"Error extracting metadata: {str(e)}", "Ollama")

    async def _call_ollama(self, prompt: str) -> str:
        """
        Make API call to Ollama service.

        Args:
            prompt: Prompt to send to model

        Returns:
            Model response

        Raises:
            APIError: If API request fails
        """
        try:
            url = f"{self.base_url}/chat"
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            }

            self.logger.debug("Calling Ollama API")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        raise APIError(
                            f"Ollama API returned status {response.status}",
                            "Ollama",
                            response.status,
                        )

                    data = await response.json()
                    return data.get("message", {}).get("content", "")

        except aiohttp.ClientError as e:
            raise APIError(f"Ollama API request failed: {str(e)}", "Ollama")
        except Exception as e:
            raise APIError(f"Error calling Ollama: {str(e)}", "Ollama")

    def _get_system_prompt(self) -> str:
        """Get system prompt for metadata extraction."""
        return """You are a specialized JSON-only responder for Document Validation and Management.
Your task is to extract metadata from academic documents.
Respond ONLY with a JSON object containing the following fields:
- authors: List of author names
- year: Publication year (integer)
- title: Document title
- doi: DOI if present
- abstract: Document abstract
- keywords: List of key topics or phrases

Format all text fields as clean, properly capitalized strings.
If a field is not found, use null.
Do not include any explanation or additional text."""

    def _construct_metadata_prompt(self, content: str) -> str:
        """
        Construct prompt for metadata extraction.

        Args:
            content: Document content

        Returns:
            Formatted prompt
        """
        # Truncate content if too long
        max_length = 2000
        if len(content) > max_length:
            content = content[:max_length] + "..."

        return f"""Extract metadata from this academic document content:

{content}

Respond with a JSON object containing authors, year, title, doi, abstract, and keywords."""

    def _parse_metadata_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured metadata.

        Args:
            response: Raw LLM response

        Returns:
            Parsed metadata

        Raises:
            APIError: If response parsing fails
        """
        try:
            # Clean up response to ensure valid JSON
            response = response.strip()
            if not response.startswith("{"):
                response = "{"
            if not response.endswith("}"):
                response += "}"

            # Parse JSON
            data = json.loads(response)

            # Validate and clean fields
            metadata = {
                "authors": self._clean_author_list(data.get("authors", [])),
                "year": self._parse_year(data.get("year")),
                "title": data.get("title", "").strip(),
                "doi": data.get("doi"),
                "abstract": data.get("abstract"),
                "keywords": self._clean_keyword_list(data.get("keywords", [])),
            }

            return metadata

        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {str(e)}", "Ollama")
        except Exception as e:
            raise APIError(f"Error parsing metadata response: {str(e)}", "Ollama")

    def _clean_author_list(self, authors: List[str]) -> List[str]:
        """Clean and validate author list."""
        if isinstance(authors, str):
            # Split string into list if needed
            authors = [a.strip() for a in authors.split(";")]

        return [
            author.strip()
            for author in authors
            if isinstance(author, str) and author.strip()
        ]

    def _clean_keyword_list(self, keywords: List[str]) -> List[str]:
        """Clean and validate keyword list."""
        if isinstance(keywords, str):
            # Split string into list if needed
            keywords = [k.strip() for k in keywords.split(",")]

        return [
            keyword.strip()
            for keyword in keywords
            if isinstance(keyword, str) and keyword.strip()
        ]

    def _parse_year(self, year: Any) -> Optional[int]:
        """Parse and validate year value."""
        if isinstance(year, int):
            return year
        elif isinstance(year, str):
            try:
                return int(year)
            except ValueError:
                return None
        return None
