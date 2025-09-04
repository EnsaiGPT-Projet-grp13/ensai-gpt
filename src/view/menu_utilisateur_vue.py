from InquirerPy import inquirer

from view.session import Session
from service.utilisateur_service import UtilisateurService


def menu_utilisateur(message: str = ""):
    """Menu Utilisateur (version fonctionnelle)
    
    Parameters
    ----------
    message : str
        Message optionnel à afficher en haut du menu (résultats, infos...)
    
    Returns
    -------
    next_view : any
        La prochaine 'vue' (fonction ou objet) à exécuter, selon ton architecture.
        Ici on renvoie soit une fonction (pour boucler), soit une autre vue.
    """
    # En-tête
    print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")
    if message:
        print(message)

    choix = inquirer.select(
        message="Faites votre choix : ",
        choices=[
            "Afficher les utilisateurs de la base de données",
            "Discuter avec une IA (choisir une personnalité)",
            "Infos de session",
            "Se déconnecter",
        ],
    ).execute()

    if choix == "Se déconnecter":
        Session().deconnexion()
        from view.accueil.accueil_vue import AccueilVue
        return AccueilVue()

    if choix == "Infos de session":
        return menu_utilisateur(Session().afficher())

    if choix == "Afficher les utilisateurs de la base de données":
        utilisateurs_str = UtilisateurService().afficher_tous()
        return menu_utilisateur(utilisateurs_str)

    if choix == "Discuter avec une IA (choisir une personnalité)":
        # Vue de sélection de personnalité, puis lancement de session de chat
        from view.chat_ai_vue import ChatAIVue  # cf. la vue fournie précédemment
        return ChatAIVue()

    # Valeur de repli
    return menu_utilisateur()
