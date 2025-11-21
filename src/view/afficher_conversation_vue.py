from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.conversation_service import ConversationService
from view.menu_utilisateur_vue import MenuUtilisateurVue
from view.parametres_conversation_vue import ParametresConversationVue


class AfficherConversationVue(VueAbstraite):
    """Vue qui liste les conversations et permet d'en choisir une."""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        try:
            self.afficher()
            print("\nListe des dernières conversations")
            print("-" * 50 + "\n")

            s = Session()
            uid = s.utilisateur.get("id_utilisateur")

            conv_svc = ConversationService()
            # Renvoie une liste de RealDictRow (donc des dict)
            conversations = conv_svc.liste_resumee_proprietaire_pour_utilisateur(
                uid, limite=25
            )

            if not conversations:
                return MenuUtilisateurVue("Vous n'avez aucune conversation.")

            choices = []
            for conv in conversations:
                # conv est un dict: clés = id_conversation, titre, updated_at, personnageIA_name
                titre = conv.get("titre") or "(sans titre)"
                perso = conv.get("personnageIA_name")
                date = conv.get("updated_at")

                label = titre
                if perso:
                    label += f" avec {perso}"
                if date:
                    label += f" ({date})"

                choices.append(
                    {
                        "name": label,
                        "value": conv["id_conversation"],  # on passe l'ID en value
                    }
                )

            choices.append({"name": "Retour", "value": None})

            conv_id = inquirer.select(
                message="Quelle conversation voulez-vous ?",
                choices=choices,
            ).execute()

            if conv_id is None:
                return MenuUtilisateurVue("Retour au menu principal.")

            # On stocke directement l'ID choisi dans la session, SANS parser le label
            s.conversation_id = conv_id

            return ParametresConversationVue()

        except Exception as e:
            print("[AfficherConversationVue] Exception :", repr(e))
            return MenuUtilisateurVue(
                "Une erreur est survenue, retour au menu principal."
            )
