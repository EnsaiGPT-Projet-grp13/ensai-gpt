from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PersonnageIA:
    id_personnageIA: Optional[int]
    name: str
    system_prompt: str
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
