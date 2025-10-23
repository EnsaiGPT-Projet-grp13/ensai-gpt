from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Conversation:
    id_conversation: Optional[int]
    id_proprio: int
    id_personnageIA: int
    titre: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    is_collab: Optional[bool] = None
    token_collab: Optional[str] = None
