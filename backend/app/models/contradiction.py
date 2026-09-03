from pydantic import BaseModel
from typing import List


class Contradiction(BaseModel):
    id: str
    description: str

    evidence_a: str
    evidence_b: str

    severity: str = "medium"

    affected_theories: List[str] = []