"""
Fuzzy matching for actor names in SOCIOTYPER.

Uses rapidfuzz for efficient fuzzy string matching against known actor catalogs.
"""

from typing import Optional, List, Dict, Tuple
import logging

from sociotyper.utils.config import DEFAULT_FUZZY_MATCH_THRESHOLD

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """
    Fuzzy string matching for actor names.

    Uses rapidfuzz's token_sort_ratio for flexible matching.
    """

    def __init__(
        self,
        actors: List[str],
        threshold: int = DEFAULT_FUZZY_MATCH_THRESHOLD,
    ):
        """
        Initialize FuzzyMatcher.

        Args:
            actors: List of known actor names to match against
            threshold: Minimum score (0-100) to accept a match
        """
        self.actors = actors
        self.threshold = threshold
        self._actor_lower_map: Dict[str, str] = {
            actor.lower(): actor for actor in actors
        }

    def match(
        self,
        name: str,
        threshold: Optional[int] = None,
    ) -> Optional[str]:
        """
        Find the best matching actor for a name.

        Args:
            name: Name to match
            threshold: Optional override for match threshold

        Returns:
            Matched actor name, or None if no match found
        """
        if not name or len(name) < 2:
            return None

        threshold = threshold if threshold is not None else self.threshold
        name_lower = name.lower().strip()

        # Exact match (case-insensitive)
        if name_lower in self._actor_lower_map:
            return self._actor_lower_map[name_lower]

        # Fuzzy match using rapidfuzz
        try:
            from rapidfuzz import fuzz, process

            result = process.extractOne(
                name,
                self.actors,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=threshold,
            )

            if result:
                matched_actor, score, _ = result
                logger.debug(f"Fuzzy matched '{name}' -> '{matched_actor}' (score: {score})")
                return matched_actor

        except ImportError:
            logger.warning(
                "rapidfuzz not installed, falling back to exact match only. "
                "Install with: pip install rapidfuzz"
            )

        return None

    def match_batch(
        self,
        names: List[str],
        threshold: Optional[int] = None,
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Match multiple names.

        Args:
            names: List of names to match
            threshold: Optional override for match threshold

        Returns:
            List of (original_name, matched_actor) tuples
        """
        return [(name, self.match(name, threshold)) for name in names]

    def add_actor(self, actor: str) -> None:
        """Add an actor to the matcher."""
        if actor not in self.actors:
            self.actors.append(actor)
            self._actor_lower_map[actor.lower()] = actor

    def remove_actor(self, actor: str) -> None:
        """Remove an actor from the matcher."""
        if actor in self.actors:
            self.actors.remove(actor)
            self._actor_lower_map.pop(actor.lower(), None)

    @property
    def actor_count(self) -> int:
        """Number of actors in the catalog."""
        return len(self.actors)


# Module-level default instance
_default_matcher: Optional[FuzzyMatcher] = None


def get_default_matcher() -> FuzzyMatcher:
    """Get or create the default fuzzy matcher with EIT actors."""
    global _default_matcher
    if _default_matcher is None:
        from sociotyper.actors import get_all_actors
        _default_matcher = FuzzyMatcher(get_all_actors())
    return _default_matcher


def fuzzy_match_actor(
    name: str,
    threshold: int = DEFAULT_FUZZY_MATCH_THRESHOLD,
) -> Optional[str]:
    """
    Convenience function to match an actor name.

    Args:
        name: Name to match
        threshold: Minimum match score (0-100)

    Returns:
        Matched actor name, or None if no match found
    """
    matcher = get_default_matcher()
    return matcher.match(name, threshold)
