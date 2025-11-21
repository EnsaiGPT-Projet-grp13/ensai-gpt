from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Utilisateur:
    id_utilisateur: Optional[int]
    prenom: str
    nom: str
    mail: str
    mdp_hash: str
    naiss: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
