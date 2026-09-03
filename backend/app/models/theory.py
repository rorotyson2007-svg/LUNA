from pydantic import BaseModel, Field
from typing import List


class Theory(BaseModel):
    id: str
    title: str
    explanation: str

    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)

    assumptions: List[str] = Field(default_factory=list)

    confidence: str = "low"
    score: float = 0.0

    # -----------------------------
    # LUNA Theory Analysis
    # -----------------------------

    robustness_score: float = 0.0

    evidence_quality: float = 0.0
    timeline_certainty: float = 0.0
    scene_certainty: float = 0.0

    missing_expected_evidence: List[str] = Field(
        default_factory=list
    )

    unresolved_contradictions: List[str] = Field(
        default_factory=list
    )