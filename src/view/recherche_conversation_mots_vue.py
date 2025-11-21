from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.conversation_service import ConversationService
from service.message_service import MessageService


class RechercheConversationMotsVue(VueAbstraite):
    """Vue de recherche des conversations par des mots clés"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Recherche de conversations par mots-clés dans les messages."""
        print("\n" + "-" * 50 + "\nHistorique\n" + "-" * 50 + "\n")
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")

        conv_svc = ConversationService()
        msg_svc = MessageService()

        # On récupère les conversations accessibles (résumées)
        conversations = conv_svc.liste_resumee_accessible_pour_utilisateur(
            id_utilisateur
        )
        if not conversations:
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue("Aucune conversation dans l'historique.")

        # Saisie des mots-clés
        mots = (
            (
                inquirer.text(
                    message="Quels mots-clés recherchez-vous dans vos anciennes conversations ? :"
                ).execute()
                or ""
            )
            .strip()
            .lower()
        )

        if not mots:
            from view.historique_vue import HistoriqueVue

            return HistoriqueVue("Recherche annulée (mots-clés vides).")

        # Recherche des messages contenant ces mots
        listes_message = msg_svc.recherche_mots_message(id_utilisateur, mots)

        if not listes_message:
            from view.historique_vue import HistoriqueVue

            return HistoriqueVue("Aucune conversation ne contient ces mots.")

        # Comptage du nombre de messages correspondants par conversation
        # conv_counts: { id_conversation -> nb_messages_trouvés }
        conv_counts: dict[int, int] = {}
        for m in listes_message:
            cid = m.get("id_conversation")
            conv_counts[cid] = conv_counts.get(cid, 0) + 1

        # Index des conversations résumées par id_conversation
        conv_index = {c.get("id_conversation"): c for c in conversations}

        # Construction des choix pour Inquirer
        choices = []
        for cid, count in conv_counts.items():
            c = conv_index.get(cid)

            titre = c.get("titre") or "(sans titre)"
            perso = (
                c.get("personnageIA_name")
                or c.get("personnage_name")
                or "Personnage inconnu"
            )

            label = f"{titre} avec {perso} ({count} occurrence(s))"
            choices.append({"name": label, "value": cid})

        if not choices:
            from view.historique_vue import HistoriqueVue

            return HistoriqueVue(
                "Aucune conversation ne contient ces mots (après filtrage)."
            )

        choices.append({"name": "Retour", "value": None})

        cid_choisi = inquirer.select(
            message="Quelle conversation voulez-vous ?",
            choices=choices,
        ).execute()

        if cid_choisi is None:
            from view.historique_vue import HistoriqueVue

            return HistoriqueVue()

        s.conversation_id = cid_choisi

        from view.parametres_conversation_vue import ParametresConversationVue

        return ParametresConversationVue()
