"""
Prompt templates for LLM-based triplet extraction.

Contains structured prompts for Mistral, Gemma, and SpaCy-LLM hybrid approaches.
"""

from typing import List, Optional
from sociotyper.utils.config import CANONICAL_VERBS_LIST


class PromptBuilder:
    """Build prompts for triplet extraction."""

    def __init__(self, canonical_verbs: Optional[List[str]] = None):
        self.canonical_verbs = canonical_verbs or CANONICAL_VERBS_LIST

    def build_extraction_prompt(self, text_chunk: str) -> str:
        """
        Build the standard extraction prompt.

        Args:
            text_chunk: Text to extract triplets from

        Returns:
            Formatted prompt string
        """
        verbs_str = ", ".join(self.canonical_verbs)

        return f"""You are an expert in extracting organizational relationship triples.

Focus ONLY on verbs related to institutional actions like:
{verbs_str}

Each triple must follow this format:
Role: [organization taking action]
Practice: [main institutional action verb — must come from the above list or its semantic equivalent]
Counterrole: [partner or recipient organization]
Context: [short quote from the text supporting the relation]

Ignore vague or non-relational verbs (e.g. "discusses", "mentions", "focuses on").

TEXT:
{text_chunk}
"""

    def build_gemma_prompt(self, text_chunk: str, user_prompt: str = "") -> str:
        """
        Build Gemma-specific prompt with chat format.

        Args:
            text_chunk: Text to extract triplets from
            user_prompt: Optional additional instructions

        Returns:
            Formatted prompt string for Gemma
        """
        base_prompt = self._build_base_prompt(text_chunk, user_prompt)

        return f"""<start_of_turn>user
{base_prompt}<end_of_turn>
<start_of_turn>model
"""

    def build_mistral_prompt(self, text_chunk: str, user_prompt: str = "") -> str:
        """
        Build Mistral-specific prompt.

        Args:
            text_chunk: Text to extract triplets from
            user_prompt: Optional additional instructions

        Returns:
            Formatted prompt string for Mistral
        """
        return self._build_base_prompt(text_chunk, user_prompt)

    def build_spacy_enhanced_prompt(
        self,
        text_chunk: str,
        entities: List[str],
        potential_roles: List[str],
        verbs: List[str],
        user_prompt: str = ""
    ) -> str:
        """
        Build prompt enhanced with SpaCy NLP preprocessing.

        Args:
            text_chunk: Text to extract triplets from
            entities: Named entities found by SpaCy
            potential_roles: Potential role actors identified
            verbs: Verbs found in text
            user_prompt: Optional additional instructions

        Returns:
            Formatted prompt string with NLP context
        """
        verbs_str = ", ".join(self.canonical_verbs)
        entities_str = ", ".join(entities[:20]) if entities else "none found"
        roles_str = ", ".join(potential_roles[:10]) if potential_roles else "none found"

        nlp_context = f"""
NLP PRE-ANALYSIS:
- Named Entities Found: {entities_str}
- Potential Organizational Roles: {roles_str}
- Key Verbs Detected: {', '.join(verbs[:10]) if verbs else 'none found'}
"""

        base_instructions = f"""You are an expert in extracting organizational relationship triples from institutional texts.

{user_prompt}

Focus ONLY on verbs related to institutional actions like:
{verbs_str}

{nlp_context}

Extract relationship triples in this EXACT JSON format:
[
  {{
    "role": "organization taking action",
    "practice": "main institutional action verb",
    "counterrole": "partner or recipient organization",
    "context": "short quote from text supporting this"
  }}
]

Rules:
1. Only include clear, explicit relationships
2. Role must be a specific organization or actor
3. Practice must be from the canonical verb list or semantically similar
4. Counterrole should be specific (not generic like "people" or "partners")
5. Context must be a direct quote from the text

TEXT TO ANALYZE:
{text_chunk}

Return ONLY the JSON array, no other text.
"""
        return base_instructions

    def _build_base_prompt(self, text_chunk: str, user_prompt: str = "") -> str:
        """Build base prompt with optional user instructions."""
        verbs_str = ", ".join(self.canonical_verbs)

        user_section = f"\nAdditional Instructions: {user_prompt}\n" if user_prompt else ""

        return f"""You are an expert in extracting organizational relationship triples from institutional texts.
{user_section}
Focus ONLY on verbs related to institutional actions like:
{verbs_str}

Extract relationship triples in this EXACT JSON format:
[
  {{
    "role": "organization taking action",
    "practice": "main institutional action verb",
    "counterrole": "partner or recipient organization",
    "context": "short quote from text supporting this"
  }}
]

Rules:
1. Only include clear, explicit relationships
2. Role must be a specific organization or actor
3. Practice must be from the canonical verb list or semantically similar
4. Counterrole should be specific (not generic like "people" or "partners")
5. Context must be a direct quote from the text

TEXT TO ANALYZE:
{text_chunk}

Return ONLY the JSON array, no other text.
"""


# Default prompt builder instance
default_prompt_builder = PromptBuilder()
