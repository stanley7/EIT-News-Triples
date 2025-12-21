"""
Flask application factory for SOCIOTYPER API.

Provides REST API endpoints for triplet extraction and validation.
"""

from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
import re

from sociotyper.validation.validator import TripletValidator
from sociotyper.validation.schemas import APITriplet, ExtractionResponse
from sociotyper.actors import get_all_actors
from sociotyper.core.chunker import chunk_text

logger = logging.getLogger(__name__)


class SociotyperAPI:
    """
    Main API class for SOCIOTYPER.

    Handles model loading, extraction, and validation.
    """

    def __init__(
        self,
        load_models: bool = False,
        models_to_load: Optional[List[str]] = None,
    ):
        """
        Initialize SociotyperAPI.

        Args:
            load_models: Whether to load LLM models on init
            models_to_load: List of model names to load ("mistral", "gemma")
        """
        self.validator = TripletValidator()
        self.actors = get_all_actors()

        # Model instances (lazy-loaded)
        self._mistral_model = None
        self._mistral_tokenizer = None
        self._gemma_model = None
        self._gemma_tokenizer = None
        self._spacy_nlp = None

        if load_models:
            self._load_models(models_to_load or ["mistral"])

    def _load_models(self, model_names: List[str]) -> None:
        """Load specified models."""
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        if "mistral" in model_names:
            logger.info("Loading Mistral 7B...")
            model_id = "mistralai/Mistral-7B-Instruct-v0.3"
            self._mistral_tokenizer = AutoTokenizer.from_pretrained(model_id)
            self._mistral_tokenizer.pad_token = self._mistral_tokenizer.eos_token
            self._mistral_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
            logger.info("Mistral loaded")

        if "gemma" in model_names:
            logger.info("Loading Gemma 7B...")
            model_id = "google/gemma-7b-it"
            self._gemma_tokenizer = AutoTokenizer.from_pretrained(model_id)
            self._gemma_tokenizer.pad_token = self._gemma_tokenizer.eos_token
            self._gemma_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
            logger.info("Gemma loaded")

    def _load_spacy(self):
        """Load spaCy model."""
        if self._spacy_nlp is None:
            import spacy
            try:
                self._spacy_nlp = spacy.load("en_core_web_sm")
            except OSError:
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self._spacy_nlp = spacy.load("en_core_web_sm")
        return self._spacy_nlp

    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models."""
        return [
            {"id": "Mistral 7B", "name": "Mistral 7B", "type": "LLM"},
            {"id": "Gemma 7B", "name": "Gemma 7B", "type": "LLM"},
            {"id": "SpacyLLM", "name": "SpaCy-LLM Hybrid", "type": "Hybrid"},
        ]

    def extract_triplets(
        self,
        text: str,
        model_name: str = "Mistral 7B",
        user_prompt: str = "",
        max_triplets: Optional[int] = None,
        chunk_size: int = 1500,
    ) -> Dict[str, Any]:
        """
        Extract triplets from text.

        Args:
            text: Input text
            model_name: Model to use ("Mistral 7B", "Gemma 7B", "SpacyLLM")
            user_prompt: Additional instructions
            max_triplets: Maximum number of triplets to extract
            chunk_size: Characters per chunk

        Returns:
            Extraction results dictionary
        """
        if not text.strip():
            return {"error": "No text provided", "status": "error"}

        # Map model name
        model_map = {
            "Mistral 7B": "mistral",
            "Gemma 7B": "gemma",
            "SpacyLLM": "spacy-llm",
        }
        model_key = model_map.get(model_name, "mistral")

        # Chunk text
        chunks = self._chunk_text_sentences(text, chunk_size)
        total_chunks = len(chunks)

        logger.info(f"Processing {total_chunks} chunks with {model_name}")

        all_triplets = []

        for i, chunk in enumerate(chunks):
            if max_triplets and len(all_triplets) >= max_triplets:
                break

            try:
                if model_key == "spacy-llm":
                    triples = self._extract_with_spacy_llm(chunk, user_prompt)
                elif model_key == "gemma":
                    triples = self._extract_with_llm(
                        chunk, user_prompt, "gemma",
                        self._gemma_tokenizer, self._gemma_model
                    )
                else:
                    triples = self._extract_with_llm(
                        chunk, user_prompt, "mistral",
                        self._mistral_tokenizer, self._mistral_model
                    )

                for triple in triples:
                    if max_triplets and len(all_triplets) >= max_triplets:
                        break
                    all_triplets.append(triple)

                time.sleep(0.3)

            except Exception as e:
                logger.error(f"Error in chunk {i + 1}: {e}")
                continue

        # Format response
        formatted = []
        for idx, triple in enumerate(all_triplets):
            formatted.append({
                "id": idx + 1,
                "text": triple.get("context", "No context"),
                "community": "EIT Community",
                "extracted": {
                    "role": triple.get("role", "Unknown"),
                    "practice": triple.get("practice", "Unknown"),
                    "counterrole": triple.get("counterrole", "Unknown"),
                },
                "confidence": triple.get("model_confidence", 0.5),
                "validated": None,
            })

        return {
            "total_chunks": total_chunks,
            "total_triplets": len(formatted),
            "triplets": formatted,
            "model_used": model_name,
            "status": "success",
        }

    def _chunk_text_sentences(self, text: str, chunk_size: int = 1500) -> List[str]:
        """Chunk text by sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks, current = [], ""

        for sent in sentences:
            if len(current) + len(sent) <= chunk_size:
                current += sent + " "
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = sent + " "

        if current.strip():
            chunks.append(current.strip())

        return chunks

    def _extract_with_llm(
        self,
        text: str,
        user_prompt: str,
        model_name: str,
        tokenizer,
        model,
    ) -> List[Dict[str, Any]]:
        """Extract triplets using LLM."""
        import torch
        import json
        import gc

        if tokenizer is None or model is None:
            logger.warning(f"Model {model_name} not loaded")
            return []

        # Build prompt
        prompt = self._make_prompt(text, user_prompt, model_name)

        try:
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=3000,
            ).to(model.device)

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=700,
                    temperature=0.5 if model_name == "gemma" else 0.3,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    return_dict_in_generate=True,
                    output_scores=True,
                )

            result = tokenizer.decode(outputs.sequences[0], skip_special_tokens=True)
            result = result.replace(prompt, "").strip()

            # Calculate confidence
            scores = outputs.scores
            token_confidences = [
                torch.max(torch.nn.functional.softmax(score[0], dim=-1)).item()
                for score in scores
            ]
            avg_confidence = sum(token_confidences) / len(token_confidences) if token_confidences else 0.5

            # Parse JSON from output
            triples = self._parse_json_output(result)

            # Validate triplets
            validated = []
            for triple in triples:
                triple["model_confidence"] = round(avg_confidence, 3)
                result_obj = self.validator.validate(triple)
                if result_obj.is_valid and result_obj.triplet:
                    validated.append(result_obj.triplet.model_dump())

            return validated

        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return []
        finally:
            torch.cuda.empty_cache()
            gc.collect()

    def _extract_with_spacy_llm(
        self,
        text: str,
        user_prompt: str,
    ) -> List[Dict[str, Any]]:
        """Extract using SpaCy-LLM hybrid approach."""
        import torch
        import json
        import gc

        if self._mistral_model is None:
            logger.warning("Mistral model not loaded for SpaCy-LLM")
            return []

        nlp = self._load_spacy()

        try:
            doc = nlp(text[:5000])

            # Extract entities
            entities = [(ent.text, ent.label_) for ent in doc.ents]

            # Find potential roles
            potential_roles = []
            text_lower = text.lower()
            for actor in self.actors[:50]:
                if actor.lower() in text_lower:
                    potential_roles.append(actor)

            # Extract verbs
            verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"][:20]

            # Build enhanced prompt
            prompt = self._make_spacy_enhanced_prompt(
                text[:2000], potential_roles, entities, verbs, user_prompt
            )

            inputs = self._mistral_tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=3000,
            ).to(self._mistral_model.device)

            with torch.no_grad():
                outputs = self._mistral_model.generate(
                    **inputs,
                    max_new_tokens=700,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=self._mistral_tokenizer.eos_token_id,
                    return_dict_in_generate=True,
                    output_scores=True,
                )

            result = self._mistral_tokenizer.decode(outputs.sequences[0], skip_special_tokens=True)
            result = result.replace(prompt, "").strip()

            scores = outputs.scores
            token_confidences = [
                torch.max(torch.nn.functional.softmax(score[0], dim=-1)).item()
                for score in scores
            ]
            avg_confidence = sum(token_confidences) / len(token_confidences) if token_confidences else 0.75

            triples = self._parse_json_output(result)

            validated = []
            for triple in triples:
                triple["model_confidence"] = round(avg_confidence, 3)
                result_obj = self.validator.validate(triple)
                if result_obj.is_valid and result_obj.triplet:
                    validated.append(result_obj.triplet.model_dump())

            return validated

        except Exception as e:
            logger.error(f"SpaCy-LLM error: {e}")
            return []
        finally:
            torch.cuda.empty_cache()
            gc.collect()

    def _make_prompt(self, text: str, user_prompt: str, model_name: str) -> str:
        """Build extraction prompt."""
        actor_examples = "\n".join([f"  • {actor}" for actor in self.actors[:30]])

        base = f"""Extract organizational relationships as JSON.

CONSTRAINT: 'role' MUST be from this list:
{actor_examples}
  • ... and {len(self.actors)-30} more actors

RULES:
1. role: Organization taking action (from list above)
2. practice: Specific action verb (e.g., "fund", "partner with", "support")
3. counterrole: Specific named entity (not generic terms)
4. context: Exact sentence

Output ONLY valid JSON array."""

        if user_prompt:
            base += f"\n\nADDITIONAL INSTRUCTIONS:\n{user_prompt}"

        base += f"\n\nTEXT:\n{text}\n\nJSON:"

        if model_name == "gemma":
            return f"<start_of_turn>user\n{base}<end_of_turn>\n<start_of_turn>model\n"

        return base

    def _make_spacy_enhanced_prompt(
        self,
        text: str,
        potential_roles: List[str],
        entities: List[tuple],
        verbs: List[str],
        user_prompt: str,
    ) -> str:
        """Build SpaCy-enhanced prompt."""
        return f"""Extract organizational relationships using NLP analysis:

DETECTED ORGANIZATIONS: {', '.join(potential_roles[:10])}
NAMED ENTITIES: {', '.join([f"{e[0]} ({e[1]})" for e in entities[:15]])}
KEY VERBS: {', '.join(verbs[:15])}

Task: Extract triplets (role → practice → counterrole)
- role: MUST be from detected organizations above
- practice: Action verb (preferably from key verbs)
- counterrole: Specific named entity (from detected entities or text)
- context: Exact sentence from text

{f"Additional: {user_prompt}" if user_prompt else ""}

Text to analyze:
{text}

Output ONLY JSON array:
[{{"role": "...", "practice": "...", "counterrole": "...", "context": "..."}}]

JSON:"""

    def _parse_json_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse JSON from LLM output."""
        import json

        clean = output

        # Remove markdown code blocks
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()

        # Remove prefixes
        for prefix in ["JSON:", "OUTPUT:"]:
            if clean.upper().startswith(prefix):
                clean = clean[len(prefix):].strip()

        # Find JSON array/object
        start = clean.find("[")
        end = clean.rfind("]")

        if start == -1:
            start = clean.find("{")
            end = clean.rfind("}")
            if start != -1 and end != -1:
                clean = "[" + clean[start:end+1] + "]"
                start, end = 0, len(clean) - 1

        if start == -1 or end == -1:
            return []

        json_text = clean[start:end+1]

        try:
            data = json.loads(json_text)
            if isinstance(data, dict):
                data = [data]
            return data
        except json.JSONDecodeError:
            return []

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape text from a URL."""
        import requests
        from bs4 import BeautifulSoup

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = [
                p.get_text().strip()
                for p in soup.find_all("p")
                if p.get_text().strip()
            ]
            text = "\n\n".join(paragraphs)

            return {"text": text, "source": url}

        except Exception as e:
            return {"error": str(e)}


def create_app(api: Optional[SociotyperAPI] = None) -> Flask:
    """
    Create Flask application.

    Args:
        api: Optional SociotyperAPI instance (creates new one if not provided)

    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    CORS(app)

    if api is None:
        api = SociotyperAPI()

    @app.route("/models", methods=["GET"])
    def get_models():
        return jsonify({"models": api.get_available_models()})

    @app.route("/extract_triplets", methods=["POST"])
    def extract_triplets():
        data = request.get_json(force=True)
        text = data.get("text", "")
        model = data.get("model", "Mistral 7B")
        user_prompt = data.get("user_prompt", "")
        max_triplets = data.get("max_triplets")

        result = api.extract_triplets(
            text=text,
            model_name=model,
            user_prompt=user_prompt,
            max_triplets=max_triplets,
        )

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)

    @app.route("/scrape_url", methods=["POST"])
    def scrape_url():
        data = request.get_json(force=True)
        url = data.get("url", "")

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        result = api.scrape_url(url)

        if "error" in result:
            return jsonify(result), 500

        return jsonify(result)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"})

    return app
