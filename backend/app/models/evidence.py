from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class Evidence(BaseModel):
    # Existing LUNA fields
    id: str
    type: str
    timestamp: str
    source: str
    location: Optional[str] = None
    observation: str

    reliability: float = 0.5

    people: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)

    metadata: Dict = Field(default_factory=dict)

    # -----------------------------
    # LUNA Evidence DNA
    # -----------------------------

    # How directly this evidence establishes an event.
    # 1.0 = direct observation
    # 0.0 = highly indirect
    directness: float = 0.5

    # Confidence in the evidence timestamp.
    timestamp_confidence: float = 0.5

    # IDs of evidence pieces this evidence depends upon.
    dependencies: List[str] = Field(default_factory=list)

    # IDs of evidence pieces that contradict this evidence.
    contradictions: List[str] = Field(default_factory=list)

    # Theories this evidence supports.
    supports_theories: List[str] = Field(default_factory=list)

    # Theories this evidence contradicts.
    refutes_theories: List[str] = Field(default_factory=list)

    # Calculated contribution of this evidence to each theory.
    # Example:
    # {
    #     "T-001": 0.32,
    #     "T-002": -0.18
    # }
    contribution_scores: Dict[str, float] = Field(default_factory=dict)

    # Evidence state.
    # active = currently used
    # disputed = challenged by another evidence item
    # excluded = deliberately removed from analysis
    status: str = "active"