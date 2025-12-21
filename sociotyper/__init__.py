"""
SOCIOTYPER - Extract organizational relationship triplets from text using AI

This package provides tools for:
- Extracting role-practice-counterrole triplets from organizational text
- Normalizing verbs to canonical institutional actions
- Validating extracted triplets against known actor catalogs
- Serving extraction via REST API
"""

__version__ = "0.1.0"
__author__ = "SOCIOTYPER Team"

from sociotyper.core.extraction import TripleExtractor
from sociotyper.core.chunker import TextChunker, chunk_text
from sociotyper.core.normalizer import VerbNormalizer, normalize_verb
from sociotyper.validation.validator import TripletValidator, validate_triplet
from sociotyper.validation.schemas import Triplet, ExtractedTriplet

__all__ = [
    "TripleExtractor",
    "TextChunker",
    "chunk_text",
    "VerbNormalizer",
    "normalize_verb",
    "TripletValidator",
    "validate_triplet",
    "Triplet",
    "ExtractedTriplet",
]
