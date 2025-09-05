from tabulate import tabulate

from utils.log_decorator import log
from utils.securite import hash_password

from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao


class UtilisateurService:
    """Classe contenant les méthodes de service des Utilisateurs"""

    @log
    def creer(self, prenom, nom, mdp, naiss, mail) -> Utilisateur:
        """Création d'un utilisateur à partir de ses attributs"""

        nouvel_utilisateur = Utilisateur(
            prenom=prenom,
            nom=nom,
            mdp=hash_password(mdp, mail),   # sel = mail
            naiss=naiss,
            mail=mail,
        )

        return nouvel_utilisateur if UtilisateurDao().creer(nouvel_utilisateur) else None

    @log
    def lister_tous(self, inclure_mdp: bool = False) -> list[Utilisateur]:
        """Lister tous les utilisateurs
        Si inclure_mdp=True, les mots de passe seront inclus
        Par défaut, tous les mdp des utilisateurs sont à None
        """
        utilisateurs = UtilisateurDao().lister_tous()
        if not inclure_mdp:
            for u in utilisateurs:
                u.mdp = None
        return utilisateurs

    @log
    def trouver_par_id(self, id_utilisateur) -> Utilisateur:
        """Trouver un utilisateur à partir de son id"""
        return UtilisateurDao().trouver_par_id(id_utilisateur)

    @log
    def modifier(self, utilisateur) -> Utilisateur:
        """Modification d'un utilisateur"""
        # Re-hash du mdp s'il est fourni en clair
        utilisateur.mdp = hash_password(utilisateur.mdp, utilisateur.mail)
        return utilisateur if UtilisateurDao().modifier(utilisateur) else None

    @log
    def supprimer(self, utilisateur) -> bool:
        """Supprimer le compte d'un utilisateur"""
        return UtilisateurDao().supprimer(utilisateur)

    @log
    def afficher_tous(self) -> str:
        """Afficher tous les utilisateurs
        Sortie : Une chaîne de caractères mise sous forme de tableau
        """
        entetes = ["prenom", "nom", "naiss", "mail"]

        utilisateurs = UtilisateurDao().lister_tous()

        # (Optionnel) Exclure un compte admin s'il existe — ici on filtre par mail
        # utilisateurs = [u for u in utilisateurs if u.mail != "admin@exemple.com"]

        utilisateurs_as_list = [u.as_list() for u in utilisateurs]

        str_users = "-" * 100
        str_users += "\nListe des utilisateurs \n"
        str_users += "-" * 100
        str_users += "\n"
        str_users += tabulate(
            tabular_data=utilisateurs_as_list,
            headers=entetes,
            tablefmt="psql",
            floatfmt=".2f",
        )
        str_users += "\n"

        return str_users

    @log
    def se_connecter(self, mail, mdp) -> Utilisateur:
        """Se connecter à partir de mail et mdp"""
        return UtilisateurDao().se_connecter(mail, hash_password(mdp, mail))


    @log
    def mail_deja_utilise(self, mail) -> bool:
        """Vérifie si le mail est déjà utilisé
        Retourne True si le mail existe déjà en BDD
        """
        utilisateurs = UtilisateurDao().lister_tous()
        return mail in [u.mail for u in utilisateurs]
