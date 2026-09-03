from typing import List

from pydantic import BaseModel, Field, field_validator


# ============================================================
# THEORY ENGINE
# ============================================================

class TheoryOutput(BaseModel):
    id: str
    title: str
    explanation: str

    supporting_evidence: List[str] = Field(
        default_factory=list
    )

    contradicting_evidence: List[str] = Field(
        default_factory=list
    )

    assumptions: List[str] = Field(
        default_factory=list
    )

    confidence: str

    score: float


class TheoryEngineOutput(BaseModel):
    theories: List[TheoryOutput]


# ============================================================
# RED TEAM
# ============================================================

class RedTeamOutput(BaseModel):

    theory_id: str

    verdict: str

    strengths: List[str] = Field(
        default_factory=list
    )

    unsupported_claims: List[str] = Field(
        default_factory=list
    )

    contradictions: List[str] = Field(
        default_factory=list
    )

    assumptions: List[str] = Field(
        default_factory=list
    )

    alternative_explanations: List[str] = Field(
        default_factory=list
    )

    critical_questions: List[str] = Field(
        default_factory=list
    )

    evidence_gaps: List[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Clean accidental placeholder responses.
    # --------------------------------------------------------

    @field_validator(
        "strengths",
        "unsupported_claims",
        "contradictions",
        "assumptions",
        "alternative_explanations",
        "critical_questions",
        "evidence_gaps",
        mode="before",
    )
    @classmethod
    def clean_lists(cls, value):

        if value is None:
            return []

        if isinstance(value, str):

            text = value.strip()

            if not text:
                return []

            return [text]

        if isinstance(value, list):

            cleaned = []

            for item in value:

                if not isinstance(item, str):
                    continue

                item = item.strip()

                if not item:
                    continue

                # Remove useless placeholder responses.
                if item.lower() in {
                    "contradictions",
                    "assumptions",
                    "evidence gaps",
                    "alternative explanations",
                    "critical questions",
                    "unsupported claims",
                    "none",
                    "n/a",
                }:
                    continue

                cleaned.append(item)

            return cleaned

        return []