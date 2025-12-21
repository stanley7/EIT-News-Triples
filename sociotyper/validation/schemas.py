"""
Pydantic schemas for SOCIOTYPER data models.

Defines structured types for triplets, validation results, and API responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Triplet(BaseModel):
    """Base triplet schema with role-practice-counterrole."""

    role: str = Field(..., description="Organization taking the action")
    practice: str = Field(..., description="Institutional action verb")
    counterrole: str = Field(..., description="Partner or recipient organization")
    context: str = Field(default="", description="Supporting quote from text")

    class Config:
        extra = "allow"


class NEREntity(BaseModel):
    """Named entity extracted from context."""

    text: str
    label: str


class ExtractedTriplet(Triplet):
    """Triplet with extraction metadata."""

    chunk_id: Optional[int] = Field(default=None, description="Source chunk ID")
    practice_original: Optional[str] = Field(
        default=None, description="Original practice before normalization"
    )
    practice_score: Optional[float] = Field(
        default=None, description="Verb normalization confidence score"
    )
    model_confidence: Optional[float] = Field(
        default=None, description="LLM generation confidence"
    )
    ner: List[NEREntity] = Field(
        default_factory=list, description="Named entities in context"
    )


class ValidationResult(BaseModel):
    """Result of triplet validation."""

    is_valid: bool
    reason: str
    triplet: Optional[ExtractedTriplet] = None


class APITriplet(BaseModel):
    """Triplet formatted for API response."""

    id: int
    text: str = Field(description="Context text")
    community: str = Field(default="EIT Community")
    extracted: Dict[str, str] = Field(
        description="Extracted triplet (role, practice, counterrole)"
    )
    confidence: float = Field(default=0.5)
    validated: Optional[bool] = None


class ExtractionResponse(BaseModel):
    """API response for extraction endpoint."""

    total_chunks: int
    total_triplets: int
    triplets: List[APITriplet]
    model_used: str
    status: str = "success"


class ModelInfo(BaseModel):
    """Model information for API."""

    id: str
    name: str
    type: str = "LLM"


class ModelsResponse(BaseModel):
    """API response for models endpoint."""

    models: List[ModelInfo]
