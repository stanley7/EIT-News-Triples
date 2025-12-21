"""
Text chunking utilities for SOCIOTYPER.

Splits text into manageable chunks for LLM processing.
"""

from typing import List, Optional
import re

from sociotyper.utils.config import DEFAULT_CHUNK_SIZE


class TextChunker:
    """
    Split text into chunks for LLM processing.

    Supports word-based and sentence-based chunking strategies.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        method: str = "word",
        overlap: int = 0
    ):
        """
        Initialize TextChunker.

        Args:
            chunk_size: Maximum size per chunk (words or characters)
            method: Chunking method - "word", "sentence", or "char"
            overlap: Number of units to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.method = method
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if self.method == "word":
            return self._chunk_by_words(text)
        elif self.method == "sentence":
            return self._chunk_by_sentences(text)
        elif self.method == "char":
            return self._chunk_by_chars(text)
        else:
            raise ValueError(f"Unknown chunking method: {self.method}")

    def _chunk_by_words(self, text: str) -> List[str]:
        """Chunk by word count."""
        chunks = []
        words = text.split()
        step = self.chunk_size - self.overlap

        for i in range(0, len(words), step):
            chunk = " ".join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk by sentences, respecting boundaries."""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())

            if current_size + sentence_words > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Keep overlap
                if self.overlap > 0:
                    overlap_text = " ".join(current_chunk[-self.overlap:])
                    current_chunk = [overlap_text]
                    current_size = len(overlap_text.split())
                else:
                    current_chunk = []
                    current_size = 0

            current_chunk.append(sentence)
            current_size += sentence_words

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _chunk_by_chars(self, text: str) -> List[str]:
        """Chunk by character count."""
        chunks = []
        step = self.chunk_size - self.overlap

        for i in range(0, len(text), step):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)

        return chunks


def chunk_text(
    text: str,
    max_words: int = DEFAULT_CHUNK_SIZE,
    method: str = "word"
) -> List[str]:
    """
    Convenience function to chunk text.

    Args:
        text: Input text to chunk
        max_words: Maximum words per chunk
        method: Chunking method

    Returns:
        List of text chunks
    """
    chunker = TextChunker(chunk_size=max_words, method=method)
    return chunker.chunk(text)
