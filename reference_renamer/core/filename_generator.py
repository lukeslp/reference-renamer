"""
Filename generation module for Reference Renamer.
Handles generation of standardized filenames from metadata.
"""

import re
from typing import Optional
import logging
import os
from pathlib import Path

from .metadata_enricher import ArticleMetadata
from ..utils.exceptions import FilenameGenerationError
from ..utils.logging import get_logger


class FilenameGenerator:
    """Generates standardized filenames from metadata."""

    def __init__(
        self,
        max_title_words: int = 5,
        separator: str = "_",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the filename generator.

        Args:
            max_title_words: Maximum number of words to use from title
            separator: Character to use for separating components
            logger: Optional logger instance
        """
        self.max_title_words = max_title_words
        self.separator = separator
        self.logger = logger or get_logger(__name__)

    def generate_filename(
        self, metadata: ArticleMetadata, original_extension: str
    ) -> str:
        """
        Generates filename in format: Author_Year_FiveWordTitle.ext

        Args:
            metadata: ArticleMetadata object
            original_extension: Original file extension

        Returns:
            Standardized filename

        Raises:
            FilenameGenerationError: If filename generation fails
        """
        try:
            # Get primary author
            author = self._format_author(
                metadata.authors[0] if metadata.authors else "Unknown"
            )

            # Format year
            year = str(metadata.year) if metadata.year else "XXXX"

            # Generate title fragment
            title = self._generate_title_fragment(metadata.title)

            # Combine and sanitize
            filename = f"{author}{self.separator}{year}{self.separator}{title}{original_extension}"
            return self._sanitize_filename(filename)

        except Exception as e:
            raise FilenameGenerationError(f"Error generating filename: {str(e)}")

    def _format_author(self, author: str) -> str:
        """
        Formats author name (Last, First -> Last).

        Args:
            author: Author name to format

        Returns:
            Formatted author name
        """
        # Handle empty author
        if not author or author == "Unknown":
            return "UnknownAuthor"

        # Split on common delimiters
        parts = re.split(r"[,;]", author)

        # Get last name
        last_name = parts[0].strip()

        # Remove non-alphanumeric characters
        last_name = re.sub(r"\W+", "", last_name)

        # Ensure valid length
        if len(last_name) < 2:
            return "UnknownAuthor"

        return last_name

    def _generate_title_fragment(self, title: str) -> str:
        """
        Generates a five-word title fragment.

        Args:
            title: Full title to process

        Returns:
            Title fragment suitable for filename
        """
        if not title:
            return "UntitledDocument"

        # Split into words
        words = title.split()

        # Select first N meaningful words
        selected_words = []
        for word in words:
            # Skip very short words and common articles
            if len(word) <= 1 or word.lower() in {
                "a",
                "an",
                "the",
                "and",
                "or",
                "but",
                "nor",
                "for",
            }:
                continue

            # Clean word
            clean_word = re.sub(r"\W+", "", word)
            if clean_word:
                selected_words.append(clean_word)

            if len(selected_words) >= self.max_title_words:
                break

        # If we don't have enough words, pad with placeholder
        while len(selected_words) < self.max_title_words:
            selected_words.append("X")

        # Capitalize each word
        selected_words = [word.capitalize() for word in selected_words]

        return self.separator.join(selected_words)

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes filename for filesystem compatibility.

        Args:
            filename: Proposed filename

        Returns:
            Sanitized filename
        """
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)

        # Replace spaces with separator
        filename = re.sub(r"\s+", self.separator, filename)

        # Remove multiple separators
        filename = re.sub(f"{self.separator}+", self.separator, filename)

        # Remove separators from start/end
        filename = filename.strip(self.separator)

        # Ensure filename isn't too long (max 255 chars is common limit)
        if len(filename) > 255:
            base, ext = os.path.splitext(filename)
            filename = base[: 255 - len(ext)] + ext

        return filename

    def validate_filename(self, filename: str, directory: Path) -> bool:
        """
        Validates if a filename is usable.

        Args:
            filename: Proposed filename
            directory: Target directory

        Returns:
            Whether the filename is valid
        """
        try:
            # Check length
            if len(filename) > 255:
                self.logger.warning("Filename too long")
                return False

            # Check if file exists
            target_path = directory / filename
            if target_path.exists():
                self.logger.warning(f"File already exists: {filename}")
                return False

            # Try to create and remove a test file
            try:
                target_path.touch()
                target_path.unlink()
                return True
            except OSError:
                self.logger.warning(f"Cannot create file with name: {filename}")
                return False

        except Exception as e:
            self.logger.error(f"Error validating filename: {str(e)}")
            return False

    def generate_unique_filename(self, base_filename: str, directory: Path) -> str:
        """
        Generates a unique filename by adding a counter if needed.

        Args:
            base_filename: Original filename
            directory: Target directory

        Returns:
            Unique filename
        """
        if not self.validate_filename(base_filename, directory):
            # Split name and extension
            base, ext = os.path.splitext(base_filename)
            counter = 1

            while counter < 1000:  # Prevent infinite loop
                new_filename = f"{base}_{counter}{ext}"
                if self.validate_filename(new_filename, directory):
                    return new_filename
                counter += 1

            raise FilenameGenerationError("Could not generate unique filename")

        return base_filename
