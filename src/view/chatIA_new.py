import os
import requests
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.menu_utilisateur_vue import MenuUtilisateurVue


class ChatNew(VueAbstraite):
    """
    Chat terminal avec l'API ENSAI GPT (sans base de données).

    - Construit et garde un historique minimal (system + échanges)
    - Appelle POST {WEBSERVICE_HOST}/generate
    - Quitter : envoyer une ligne vide
    """

    def __init__(self, first_user_message: str, system_prompt: str | None = None) -> None:
        host = os.getenv(
            "WEBSERVICE_HOST",
            "https://ensai-gpt-109912438483.europe-west4.run.app",
        ).rstrip("/")
        self.api_url = f"{host}/generate"

        self.system_prompt = system_prompt or "Tu es un assistant utile."
        self.history = [
            {"role": "system", "content": self.system_prompt},
        ]
        if first_user_message:
            self.history.append({"role": "user", "content": first_user_message})

    def _call_api(self) -> str:
        """Appelle l'API et renvoie le texte de réponse (string)."""
        payload = {
            "history": self.history,
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "top_p": float(os.getenv("LLM_TOP_P", "1.0")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "300")),
        }
        try:
            r = requests.post(self.api_url, json=payload, timeout=30)
        except Exception as e:
            return f"[Erreur réseau] {e}"

        if r.status_code != 200:
            # essaie d'afficher le détail renvoyé
            msg = r.text
            try:
                msg = r.json()
            except Exception:
                pass
            return f"[Erreur HTTP {r.status_code}] {msg}"

        # D'après la doc, le 200 renvoie un JSON simple (string)
        try:
            data = r.json()
        except Exception:
            return f"[Erreur parsing] Réponse non JSON: {r.text}"

        # Supporte soit un string brut, soit un dict avec 'content'
        if isinstance(data, str):
            return data
        if isinstance(data, dict) and "content" in data:
            return data["content"]

        return str(data)

    def choisir_menu(self):
        """Boucle d'échange : une réponse, puis on redemande; vide => retour menu."""
        # Si on a une première question, on envoie
        if len(self.history) > 1 and self.history[-1]["role"] == "user":
            answer = self._call_api()
            print("\n--- Réponse de l'IA ---\n")
            print(answer)
            self.history.append({"role": "assistant", "content": answer})

        # Boucle
        while True:
            user_msg = inquirer.text(message="Ton message (Entrée pour quitter) :").execute()
            if not user_msg.strip():
                # retour menu utilisateur
                return MenuUtilisateurVue("Chat terminé.")

            # ajoute et envoie
            self.history.append({"role": "user", "content": user_msg})
            answer = self._call_api()
            print("\n--- Réponse de l'IA ---\n")
            print(answer)
            self.history.append({"role": "assistant", "content": answer})
