from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
    id_message: Optional[int]
    id_conversation: int
    expediteur: str              
    contenu: str
    id_utilisateur: Optional[int] = None
    created_at: Optional[datetime] = None
