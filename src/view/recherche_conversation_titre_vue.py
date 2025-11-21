from InquirerPy import inquirer

from objects.session import Session
from service.conversation_service import ConversationService
from view.vue_abstraite import VueAbstraite


class RechercheConversationTitreVue(VueAbstraite):
    """Vue de recherche des conversations par titre."""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        print(
            "\n" + "-" * 50 + "\nRecherche conversation par titre\n" + "-" * 50 + "\n"
        )
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")

        conv_svc = ConversationService()

        conversations = conv_svc.liste_resumee_accessible_pour_utilisateur(
            id_utilisateur
        )
        if not conversations:
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue("Aucune conversation dans l'historique.")

        mots = (
            (inquirer.text(message="Quel titre recherchez-vous ? :").execute() or "")
            .strip()
            .lower()
        )

        if not mots:
            from view.historique_vue import HistoriqueVue

            return HistoriqueVue("Recherche annulée (titre vide).")

        listes_titres = conv_svc.recherche_mots_titre(id_utilisateur, mots)

        if not listes_titres:
            from view.historique_vue import HistoriqueVue

            return HistoriqueVue(
                "Aucune conversation ne contient ces mots dans le titre."
            )

        choices = []
        for c in listes_titres:
            cid = c.get("id_conversation")
            titre = c.get("titre") or "(sans titre)"
            perso = (
                c.get("personnageIA_name")
                or c.get("personnage_name")
                or "Personnage inconnu"
            )

            label = f"{titre} avec {perso}"
            choices.append({"name": label, "value": cid})

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
