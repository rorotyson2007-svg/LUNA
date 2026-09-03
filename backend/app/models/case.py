from pydantic import BaseModel
from typing import List

from .evidence import Evidence
from .event import Event
from .person import Person
from .theory import Theory
from .contradiction import Contradiction


class Case(BaseModel):
    id: str
    title: str
    description: str

    evidence: List[Evidence] = []
    events: List[Event] = []
    people: List[Person] = []

    contradictions: List[Contradiction] = []
    theories: List[Theory] = []