"""
Triplet validation for SOCIOTYPER.

Validates extracted triplets against rules and known actor catalogs.
"""

from typing import Dict, Any, Optional, Tuple, List
import logging

from sociotyper.validation.schemas import ExtractedTriplet, ValidationResult
from sociotyper.validation.fuzzy_matcher import FuzzyMatcher, fuzzy_match_actor
from sociotyper.utils.config import (
    GENERIC_COUNTERROLES,
    GENERIC_ROLES,
    VAGUE_PRACTICES,
    DEFAULT_FUZZY_MATCH_THRESHOLD,
)

logger = logging.getLogger(__name__)


class TripletValidator:
    """
    Validate extracted triplets against rules and actor catalogs.

    Checks for:
    - Required fields present
    - Field length constraints
    - Generic/vague terms filtering
    - Actor catalog matching
    """

    def __init__(
        self,
        actors: Optional[List[str]] = None,
        fuzzy_threshold: int = DEFAULT_FUZZY_MATCH_THRESHOLD,
        require_actor_match: bool = True,
        filter_generic: bool = True,
    ):
        """
        Initialize TripletValidator.

        Args:
            actors: List of known actors for fuzzy matching
            fuzzy_threshold: Minimum score for actor matching
            require_actor_match: Whether role must match a known actor
            filter_generic: Whether to filter generic counterroles
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.require_actor_match = require_actor_match
        self.filter_generic = filter_generic

        # Initialize fuzzy matcher if actors provided
        if actors:
            self._matcher = FuzzyMatcher(actors, fuzzy_threshold)
        else:
            self._matcher = None

    @property
    def matcher(self) -> FuzzyMatcher:
        """Lazy-load matcher with default actors."""
        if self._matcher is None:
            from sociotyper.actors import get_all_actors
            self._matcher = FuzzyMatcher(get_all_actors(), self.fuzzy_threshold)
        return self._matcher

    def validate(
        self,
        triplet: Dict[str, Any],
    ) -> ValidationResult:
        """
        Validate a triplet.

        Args:
            triplet: Triplet dictionary to validate

        Returns:
            ValidationResult with is_valid, reason, and optionally corrected triplet
        """
        # Extract fields
        role_raw = triplet.get("role", "")
        counterrole_raw = triplet.get("counterrole", "")
        practice = triplet.get("practice", "")

        # Check required fields
        if not role_raw or not counterrole_raw or not practice:
            return ValidationResult(
                is_valid=False,
                reason="Missing required fields",
            )

        # Clean fields
        role_raw = str(role_raw).strip()
        counterrole_raw = str(counterrole_raw).strip()
        practice = str(practice).strip()

        # Check field lengths
        if len(role_raw) < 2:
            return ValidationResult(
                is_valid=False,
                reason="Role too short",
            )

        if len(counterrole_raw) < 3:
            return ValidationResult(
                is_valid=False,
                reason="Counterrole too short",
            )

        if len(counterrole_raw) > 100:
            return ValidationResult(
                is_valid=False,
                reason="Counterrole too long",
            )

        # Check for generic counterroles
        if self.filter_generic:
            counterrole_lower = counterrole_raw.lower()
            if counterrole_lower in GENERIC_COUNTERROLES:
                return ValidationResult(
                    is_valid=False,
                    reason="Generic counterrole",
                )

        # Check for vague practices
        if practice.lower() in VAGUE_PRACTICES:
            return ValidationResult(
                is_valid=False,
                reason="Vague practice verb",
            )

        # Fuzzy match role against actor catalog
        if self.require_actor_match:
            matched_role = self.matcher.match(role_raw, self.fuzzy_threshold)
            if not matched_role:
                return ValidationResult(
                    is_valid=False,
                    reason="Role not in actor catalog",
                )
            # Update role to matched version
            triplet["role"] = matched_role
        else:
            triplet["role"] = role_raw

        triplet["counterrole"] = counterrole_raw
        triplet["practice"] = practice

        # Create validated triplet
        validated = ExtractedTriplet(
            role=triplet.get("role", ""),
            practice=triplet.get("practice", ""),
            counterrole=triplet.get("counterrole", ""),
            context=triplet.get("context", ""),
            chunk_id=triplet.get("chunk_id"),
            practice_original=triplet.get("practice_original"),
            practice_score=triplet.get("practice_score"),
            model_confidence=triplet.get("model_confidence"),
            ner=triplet.get("ner", []),
        )

        return ValidationResult(
            is_valid=True,
            reason="valid",
            triplet=validated,
        )

    def validate_batch(
        self,
        triplets: List[Dict[str, Any]],
    ) -> Tuple[List[ExtractedTriplet], List[ValidationResult]]:
        """
        Validate multiple triplets.

        Args:
            triplets: List of triplet dictionaries

        Returns:
            Tuple of (valid_triplets, all_results)
        """
        valid_triplets = []
        all_results = []

        for triplet in triplets:
            result = self.validate(triplet)
            all_results.append(result)
            if result.is_valid and result.triplet:
                valid_triplets.append(result.triplet)

        logger.info(
            f"Validated {len(triplets)} triplets: "
            f"{len(valid_triplets)} valid, {len(triplets) - len(valid_triplets)} filtered"
        )

        return valid_triplets, all_results


# Module-level default validator
_default_validator: Optional[TripletValidator] = None


def get_validator() -> TripletValidator:
    """Get or create the default validator."""
    global _default_validator
    if _default_validator is None:
        _default_validator = TripletValidator()
    return _default_validator


def validate_triplet(
    triplet: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Convenience function to validate a triplet.

    Args:
        triplet: Triplet dictionary to validate

    Returns:
        Tuple of (validated_triplet_dict, reason_string)
        Returns (None, reason) if invalid
    """
    validator = get_validator()
    result = validator.validate(triplet)

    if result.is_valid and result.triplet:
        return result.triplet.model_dump(), result.reason
    else:
        return None, result.reason
