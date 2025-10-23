import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session

class MenuUtilisateurVue(VueAbstraite):
    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        try:
            print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")
            choix = inquirer.select(
                message="Faites votre choix : ",
                choices=[
                    "Démarrer un chat",
                    "Historique",
                    "Statistiques",
                    "Paramètres",
                    "Se déconnecter",
                ],
            ).execute()

            if choix == "Se déconnecter":
                Session().deconnexion()
                from view.accueil_vue import AccueilVue
                return AccueilVue("Déconnecté. À bientôt !")

            if choix == "Paramètres":
                pass
                # from view.parametres_vue import ParametresVue
                # return ParametresVue
            
            if choix == "Historique":
                from view.historique_vue import HistoriqueVue
                return HistoriqueVue()

            if choix == "Statistiques":
                pass
                # from view.statistiques_vue import StatistiquesVue
                # return HistoriqueVue()

            if choix == "Démarrer un chat":
                sous = inquirer.select(
                    message="Choisir une option :",
                    choices=[
                        "Choisir un personnage",
                        "Créer un personnage",
                        "Annuler",
                    ],
                ).execute()

                if sous == "Choisir un personnage":
                    from view.choisir_personnage_vue import ChoisirPersonnageVue
                    return ChoisirPersonnageVue()

                if sous == "Créer un personnage":
                    from view.creer_personnage_vue import CreerPersonnageVue
                    return CreerPersonnageVue()

                return MenuUtilisateurVue("Opération annulée.")

            if choix == "Reprendre un chat":
                from view.reprendre_chat_vue import ReprendreChatVue
                return ReprendreChatVue()


            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[MenuUtilisateurVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.accueil_vue import AccueilVue
            return AccueilVue("Erreur dans le menu utilisateur (voir terminal).")
