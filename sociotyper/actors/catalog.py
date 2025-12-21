"""
Actor catalog management for SOCIOTYPER.

Provides access to known EIT ecosystem actors organized by category.
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

# Path to default actors data
_ACTORS_DATA_PATH = Path(__file__).parent / "data" / "actors.json"


class ActorCatalog:
    """
    Manage a catalog of known organizational actors.

    Actors are organized by category (EIT Organizations, Universities, etc.)
    """

    def __init__(self, actors_by_category: Optional[Dict[str, List[str]]] = None):
        """
        Initialize ActorCatalog.

        Args:
            actors_by_category: Dictionary mapping category names to actor lists.
                               If None, loads from default actors.json.
        """
        if actors_by_category is None:
            actors_by_category = self._load_default_actors()

        self._actors_by_category = actors_by_category
        self._all_actors: Optional[List[str]] = None
        self._actor_to_category: Optional[Dict[str, str]] = None

    @staticmethod
    def _load_default_actors() -> Dict[str, List[str]]:
        """Load actors from the default JSON file."""
        try:
            with open(_ACTORS_DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Actors file not found: {_ACTORS_DATA_PATH}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing actors JSON: {e}")
            return {}

    @property
    def all_actors(self) -> List[str]:
        """Get flat list of all actors."""
        if self._all_actors is None:
            self._all_actors = []
            for actors in self._actors_by_category.values():
                self._all_actors.extend(actors)
        return self._all_actors

    @property
    def actor_to_category(self) -> Dict[str, str]:
        """Get mapping from actor name to category."""
        if self._actor_to_category is None:
            self._actor_to_category = {}
            for category, actors in self._actors_by_category.items():
                for actor in actors:
                    self._actor_to_category[actor] = category
        return self._actor_to_category

    @property
    def categories(self) -> List[str]:
        """Get list of category names."""
        return list(self._actors_by_category.keys())

    def get_actors(self, category: str) -> List[str]:
        """
        Get actors in a specific category.

        Args:
            category: Category name

        Returns:
            List of actor names in that category
        """
        return self._actors_by_category.get(category, [])

    def get_category(self, actor: str) -> Optional[str]:
        """
        Get the category for an actor.

        Args:
            actor: Actor name

        Returns:
            Category name, or None if actor not found
        """
        return self.actor_to_category.get(actor)

    def contains(self, actor: str) -> bool:
        """Check if an actor is in the catalog."""
        return actor in self.actor_to_category

    def search(self, query: str) -> List[str]:
        """
        Search for actors matching a query.

        Args:
            query: Search query (case-insensitive substring match)

        Returns:
            List of matching actor names
        """
        query_lower = query.lower()
        return [
            actor for actor in self.all_actors
            if query_lower in actor.lower()
        ]

    def add_actor(self, actor: str, category: str) -> None:
        """
        Add an actor to the catalog.

        Args:
            actor: Actor name
            category: Category to add to
        """
        if category not in self._actors_by_category:
            self._actors_by_category[category] = []

        if actor not in self._actors_by_category[category]:
            self._actors_by_category[category].append(actor)
            # Invalidate caches
            self._all_actors = None
            self._actor_to_category = None

    def remove_actor(self, actor: str) -> bool:
        """
        Remove an actor from the catalog.

        Args:
            actor: Actor name to remove

        Returns:
            True if actor was removed, False if not found
        """
        for category, actors in self._actors_by_category.items():
            if actor in actors:
                actors.remove(actor)
                # Invalidate caches
                self._all_actors = None
                self._actor_to_category = None
                return True
        return False

    def save(self, path: Optional[Path] = None) -> None:
        """
        Save the catalog to a JSON file.

        Args:
            path: Output path (defaults to actors.json)
        """
        path = path or _ACTORS_DATA_PATH
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._actors_by_category, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(self.all_actors)} actors to {path}")

    @classmethod
    def load(cls, path: Path) -> "ActorCatalog":
        """
        Load a catalog from a JSON file.

        Args:
            path: Path to JSON file

        Returns:
            ActorCatalog instance
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    def __len__(self) -> int:
        return len(self.all_actors)

    def __contains__(self, actor: str) -> bool:
        return self.contains(actor)

    def __repr__(self) -> str:
        return f"ActorCatalog({len(self)} actors in {len(self.categories)} categories)"


# Module-level default catalog
_default_catalog: Optional[ActorCatalog] = None


def get_catalog() -> ActorCatalog:
    """Get the default actor catalog."""
    global _default_catalog
    if _default_catalog is None:
        _default_catalog = ActorCatalog()
    return _default_catalog


def get_all_actors() -> List[str]:
    """Get flat list of all actors from the default catalog."""
    return get_catalog().all_actors


def get_actors_by_category(category: str) -> List[str]:
    """Get actors in a specific category from the default catalog."""
    return get_catalog().get_actors(category)
