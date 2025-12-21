"""
Configuration constants and settings for SOCIOTYPER.

Contains canonical verbs, model configurations, and default parameters.
"""

from typing import Set, Dict, Any
import os

# =============================================================================
# CANONICAL VERBS
# =============================================================================
# These are the institutional action verbs used for normalization.
# Extracted verbs are matched against this set using semantic similarity.

CANONICAL_VERBS: Set[str] = {
    # Funding & Investment
    "fund", "finance", "grant", "invest", "support", "sponsor", "award",
    # Partnership & Collaboration
    "partner", "collaborate", "work", "team", "ally", "join",
    # Creation & Establishment
    "create", "launch", "develop", "establish", "build", "initiate",
    "set up", "start", "found", "open", "introduce",
    # Service & Education
    "provide", "offer", "deliver", "train", "educate", "enable",
    # Growth & Support
    "accelerate", "incubate", "scale", "facilitate", "connect",
    # Management & Organization
    "select", "mentor", "coach", "coordinate", "manage",
    "operate", "organize", "implement", "run", "mobilize",
    # Advocacy & Innovation
    "campaign", "advocate", "host", "innovate", "research", "pilot", "test"
}

CANONICAL_VERBS_LIST = sorted(list(CANONICAL_VERBS))

# =============================================================================
# DEFAULT PARAMETERS
# =============================================================================

DEFAULT_CHUNK_SIZE = 900  # words per chunk
DEFAULT_SIMILARITY_THRESHOLD = 0.3  # minimum cosine similarity for verb matching
DEFAULT_FUZZY_MATCH_THRESHOLD = 60  # rapidfuzz threshold for actor matching

# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "mistral": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
        "torch_dtype": "float16",
        "max_new_tokens": 400,
        "temperature": 0.3,
        "top_p": 0.9,
    },
    "gemma": {
        "model_id": "google/gemma-7b-it",
        "torch_dtype": "float16",
        "max_new_tokens": 400,
        "temperature": 0.3,
        "top_p": 0.9,
    },
}

EMBEDDER_MODEL = "sentence-transformers/all-mpnet-base-v2"
SPACY_MODEL = "en_core_web_sm"
SPACY_MODEL_TRANSFORMER = "en_core_web_trf"

# =============================================================================
# NER LABELS
# =============================================================================

RELEVANT_NER_LABELS = {"ORG", "INSTITUTION", "GPE"}

# =============================================================================
# GENERIC TERMS TO FILTER
# =============================================================================

GENERIC_COUNTERROLES = {
    "people", "partners", "community", "stakeholders", "members",
    "participants", "organizations", "institutions", "entities",
    "others", "them", "they", "it", "we", "us"
}

GENERIC_ROLES = {
    "the organization", "the company", "it", "they", "we"
}

VAGUE_PRACTICES = {
    "has", "is", "are", "was", "were", "be", "been",
    "discusses", "mentions", "focuses on", "refers to"
}


# =============================================================================
# CONFIG CLASS
# =============================================================================

class Config:
    """Configuration manager for SOCIOTYPER."""

    def __init__(self):
        self.chunk_size = int(os.getenv("SOCIOTYPER_CHUNK_SIZE", DEFAULT_CHUNK_SIZE))
        self.similarity_threshold = float(
            os.getenv("SOCIOTYPER_SIMILARITY_THRESHOLD", DEFAULT_SIMILARITY_THRESHOLD)
        )
        self.fuzzy_threshold = int(
            os.getenv("SOCIOTYPER_FUZZY_THRESHOLD", DEFAULT_FUZZY_MATCH_THRESHOLD)
        )
        self.spacy_model = os.getenv("SOCIOTYPER_SPACY_MODEL", SPACY_MODEL)
        self.embedder_model = os.getenv("SOCIOTYPER_EMBEDDER_MODEL", EMBEDDER_MODEL)

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Export config as dictionary."""
        return {
            "chunk_size": self.chunk_size,
            "similarity_threshold": self.similarity_threshold,
            "fuzzy_threshold": self.fuzzy_threshold,
            "spacy_model": self.spacy_model,
            "embedder_model": self.embedder_model,
        }


# Global default config instance
default_config = Config()
