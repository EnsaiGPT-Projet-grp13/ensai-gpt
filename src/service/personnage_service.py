from typing import Dict, Any, List
from src.objects.personnage_ia import PersonnageIA

class PersonnageService:
    @staticmethod
    def build_payload(
        personnage: PersonnageIA,
        user_messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 150,
    ) -> Dict[str, Any]:
        history = [{"role": "system", "content": personnage.system_prompt}]
        history.extend(user_messages)
        return {
            "history": history,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
