"""
Triple extraction pipeline for SOCIOTYPER.

Orchestrates the full extraction process from text to validated triplets.
"""

from typing import List, Dict, Any, Optional, Iterator
import re
import json
import logging

from sociotyper.core.chunker import TextChunker, chunk_text
from sociotyper.core.normalizer import VerbNormalizer, normalize_verb
from sociotyper.utils.prompts import PromptBuilder
from sociotyper.utils.config import DEFAULT_CHUNK_SIZE

logger = logging.getLogger(__name__)


# Regex pattern to extract triplet components from LLM output
TRIPLE_PATTERN = re.compile(
    r"Role:\s*(.+?)\s*"
    r"Practice:\s*(.+?)\s*"
    r"Counterrole:\s*(.+?)\s*"
    r"Context:\s*(.+?)(?=Role:|$)",
    re.DOTALL | re.IGNORECASE
)


class TripleExtractor:
    """
    Extract organizational relationship triplets from text.

    Combines text chunking, LLM generation, and verb normalization.
    """

    def __init__(
        self,
        model_name: str = "mistral",
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        normalize_verbs: bool = True,
        enrich_with_ner: bool = True,
    ):
        """
        Initialize TripleExtractor.

        Args:
            model_name: LLM model to use ("mistral", "gemma", or "spacy-llm")
            chunk_size: Words per text chunk
            normalize_verbs: Whether to normalize extracted verbs
            enrich_with_ner: Whether to add NER annotations
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.normalize_verbs = normalize_verbs
        self.enrich_with_ner = enrich_with_ner

        # Lazy-loaded components
        self._model = None
        self._tokenizer = None
        self._pipe = None
        self._normalizer = None
        self._nlp = None
        self._prompt_builder = PromptBuilder()

    @property
    def normalizer(self) -> VerbNormalizer:
        """Lazy-load verb normalizer."""
        if self._normalizer is None:
            self._normalizer = VerbNormalizer()
        return self._normalizer

    def extract(
        self,
        text: str,
        user_prompt: str = "",
        progress_callback: Optional[callable] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract triplets from text.

        Args:
            text: Input text to analyze
            user_prompt: Optional additional instructions
            progress_callback: Optional callback(current, total) for progress

        Returns:
            List of extracted triplets with metadata
        """
        # Chunk the text
        chunks = chunk_text(text, max_words=self.chunk_size)
        logger.info(f"Split text into {len(chunks)} chunks")

        all_triplets = []

        for i, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(i + 1, len(chunks))

            try:
                chunk_triplets = self._extract_from_chunk(chunk, user_prompt)
                all_triplets.extend(chunk_triplets)
            except Exception as e:
                logger.error(f"Error extracting from chunk {i + 1}: {e}")
                continue

        logger.info(f"Extracted {len(all_triplets)} triplets total")
        return all_triplets

    def extract_streaming(
        self,
        text: str,
        user_prompt: str = "",
    ) -> Iterator[Dict[str, Any]]:
        """
        Extract triplets with streaming output.

        Yields triplets as they are extracted from each chunk.

        Args:
            text: Input text to analyze
            user_prompt: Optional additional instructions

        Yields:
            Extracted triplets one at a time
        """
        chunks = chunk_text(text, max_words=self.chunk_size)

        for i, chunk in enumerate(chunks):
            try:
                chunk_triplets = self._extract_from_chunk(chunk, user_prompt)
                for triplet in chunk_triplets:
                    triplet["chunk_id"] = i + 1
                    yield triplet
            except Exception as e:
                logger.error(f"Error in chunk {i + 1}: {e}")
                continue

    def _extract_from_chunk(
        self,
        chunk: str,
        user_prompt: str = ""
    ) -> List[Dict[str, Any]]:
        """Extract triplets from a single chunk."""
        # Build prompt
        prompt = self._prompt_builder.build_extraction_prompt(chunk)

        # Generate with LLM (placeholder - actual model integration in models/)
        generated_text = self._generate(prompt)

        # Parse triplets from output
        triplets = self._parse_triplets(generated_text)

        # Normalize verbs if enabled
        if self.normalize_verbs:
            triplets = self._normalize_triplet_verbs(triplets)

        # Enrich with NER if enabled
        if self.enrich_with_ner:
            triplets = self._enrich_with_ner(triplets)

        return triplets

    def _generate(self, prompt: str) -> str:
        """
        Generate text using the LLM.

        This is a placeholder - actual implementation in sociotyper.models.
        """
        # For now, return empty - actual models will override this
        logger.warning(
            "Using base TripleExtractor._generate() - "
            "use MistralExtractor or GemmaExtractor for actual extraction"
        )
        return ""

    def _parse_triplets(self, text: str) -> List[Dict[str, Any]]:
        """Parse triplets from LLM output text."""
        triplets = []

        # Try JSON parsing first
        try:
            # Find JSON array in text
            json_match = re.search(r'\[[\s\S]*\]', text)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    for item in parsed:
                        if all(k in item for k in ["role", "practice", "counterrole"]):
                            triplets.append({
                                "role": str(item.get("role", "")).strip(),
                                "practice": str(item.get("practice", "")).strip(),
                                "counterrole": str(item.get("counterrole", "")).strip(),
                                "context": str(item.get("context", "")).strip(),
                            })
                    return triplets
        except json.JSONDecodeError:
            pass

        # Fall back to regex parsing
        matches = TRIPLE_PATTERN.findall(text)
        for role, practice, counterrole, context in matches:
            triplets.append({
                "role": role.strip(),
                "practice": practice.strip(),
                "counterrole": counterrole.strip(),
                "context": context.strip(),
            })

        return triplets

    def _normalize_triplet_verbs(
        self,
        triplets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Normalize practice verbs in triplets."""
        normalized = []

        for triplet in triplets:
            practice = triplet.get("practice", "")
            norm_verb, score = self.normalizer.normalize(practice)

            if norm_verb:
                triplet["practice"] = norm_verb
                triplet["practice_original"] = practice
                triplet["practice_score"] = score
                normalized.append(triplet)
            else:
                logger.debug(f"Filtered triplet with unmatched verb: {practice}")

        return normalized

    def _enrich_with_ner(
        self,
        triplets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add NER annotations to triplet contexts."""
        if self._nlp is None:
            try:
                import spacy
                try:
                    self._nlp = spacy.load("en_core_web_trf")
                except OSError:
                    self._nlp = spacy.load("en_core_web_sm")
            except ImportError:
                logger.warning("SpaCy not available, skipping NER enrichment")
                return triplets

        for triplet in triplets:
            context = triplet.get("context", "")
            if context:
                doc = self._nlp(context)
                triplet["ner"] = [
                    {"text": ent.text, "label": ent.label_}
                    for ent in doc.ents
                    if ent.label_ in {"ORG", "INSTITUTION", "GPE", "PERSON"}
                ]

        return triplets
