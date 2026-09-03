from pydantic import BaseModel, Field
from typing import Optional


class Person(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    identity_locked: bool = True