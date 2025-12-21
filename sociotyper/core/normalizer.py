"""
Verb normalization for SOCIOTYPER.

Normalizes extracted verbs to canonical institutional action verbs
using semantic similarity.
"""

from typing import List, Optional, Tuple, Set
import logging

from sociotyper.utils.config import (
    CANONICAL_VERBS,
    CANONICAL_VERBS_LIST,
    DEFAULT_SIMILARITY_THRESHOLD,
    EMBEDDER_MODEL,
)

logger = logging.getLogger(__name__)


class VerbNormalizer:
    """
    Normalize verbs to canonical institutional actions using semantic similarity.

    Uses SentenceTransformer embeddings to find the closest canonical verb.
    """

    def __init__(
        self,
        canonical_verbs: Optional[Set[str]] = None,
        threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        embedder_model: str = EMBEDDER_MODEL,
    ):
        """
        Initialize VerbNormalizer.

        Args:
            canonical_verbs: Set of canonical verbs to normalize to
            threshold: Minimum similarity score to accept a match
            embedder_model: SentenceTransformer model name
        """
        self.canonical_verbs = sorted(list(canonical_verbs or CANONICAL_VERBS))
        self.threshold = threshold
        self.embedder_model = embedder_model

        # Lazy-loaded components
        self._embedder = None
        self._canonical_embeddings = None

    @property
    def embedder(self):
        """Lazy-load the SentenceTransformer model."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedder model: {self.embedder_model}")
                self._embedder = SentenceTransformer(self.embedder_model)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for verb normalization. "
                    "Install with: pip install sentence-transformers"
                )
        return self._embedder

    @property
    def canonical_embeddings(self):
        """Lazy-compute canonical verb embeddings."""
        if self._canonical_embeddings is None:
            self._canonical_embeddings = self.embedder.encode(
                self.canonical_verbs,
                convert_to_tensor=True,
                normalize_embeddings=True
            )
        return self._canonical_embeddings

    def normalize(
        self,
        phrase: str,
        threshold: Optional[float] = None
    ) -> Tuple[Optional[str], float]:
        """
        Normalize a verb phrase to the closest canonical verb.

        Args:
            phrase: Verb phrase to normalize
            threshold: Optional override for similarity threshold

        Returns:
            Tuple of (normalized_verb, similarity_score)
            Returns (None, score) if below threshold
        """
        import torch
        from sentence_transformers import util

        threshold = threshold if threshold is not None else self.threshold

        # Embed the input phrase
        phrase_embedding = self.embedder.encode(
            phrase,
            convert_to_tensor=True,
            normalize_embeddings=True
        )

        # Compute similarity scores
        scores = util.cos_sim(phrase_embedding, self.canonical_embeddings)

        # Find best match
        best_idx = torch.argmax(scores).item()
        best_verb = self.canonical_verbs[best_idx]
        best_score = scores[0][best_idx].item()

        if best_score < threshold:
            logger.debug(
                f"Verb '{phrase}' below threshold: {best_score:.3f} < {threshold}"
            )
            return None, best_score

        logger.debug(
            f"Normalized '{phrase}' -> '{best_verb}' (score: {best_score:.3f})"
        )
        return best_verb, best_score

    def normalize_batch(
        self,
        phrases: List[str],
        threshold: Optional[float] = None
    ) -> List[Tuple[Optional[str], float]]:
        """
        Normalize multiple verb phrases.

        Args:
            phrases: List of verb phrases to normalize
            threshold: Optional override for similarity threshold

        Returns:
            List of (normalized_verb, similarity_score) tuples
        """
        return [self.normalize(phrase, threshold) for phrase in phrases]

    def is_canonical(self, verb: str) -> bool:
        """Check if a verb is already canonical."""
        return verb.lower() in {v.lower() for v in self.canonical_verbs}


# Module-level normalizer instance (lazy-loaded)
_default_normalizer: Optional[VerbNormalizer] = None


def get_normalizer() -> VerbNormalizer:
    """Get or create the default normalizer instance."""
    global _default_normalizer
    if _default_normalizer is None:
        _default_normalizer = VerbNormalizer()
    return _default_normalizer


def normalize_verb(
    phrase: str,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD
) -> Tuple[Optional[str], float]:
    """
    Convenience function to normalize a verb phrase.

    Args:
        phrase: Verb phrase to normalize
        threshold: Minimum similarity score

    Returns:
        Tuple of (normalized_verb, similarity_score)
    """
    normalizer = get_normalizer()
    return normalizer.normalize(phrase, threshold)
