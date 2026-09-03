from pydantic import BaseModel
from typing import List, Optional


class Event(BaseModel):
    id: str
    timestamp: str
    event_type: str
    description: str

    evidence_ids: List[str] = []

    people: List[str] = []
    objects: List[str] = []
    location: Optional[str] = None