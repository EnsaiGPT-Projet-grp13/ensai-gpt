import logging

from utils.singleton import Singleton
from utils.log_decorator import log

from dao.db_connection import DBConnection

from business_object.utilisateur import Utilisateur


class UtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Utilisateurs de la base de données"""

    @log
    def creer(self, utilisateur) -> bool:
        """Création d'un utilisateur dans la base de données"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO utilisateur(prenom, nom, mdp, naiss, mail) "
                        "VALUES (%(prenom)s, %(nom)s, %(mdp)s, %(naiss)s, %(mail)s) "
                        "RETURNING id_utilisateur;",
                        {
                            "prenom": utilisateur.prenom,
                            "nom": utilisateur.nom,
                            "mdp": utilisateur.mdp,
                            "naiss": utilisateur.naiss,
                            "mail": utilisateur.mail,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        if res:
            utilisateur.id_utilisateur = res["id_utilisateur"]
            return True
        return False

    @log
    def trouver_par_id(self, id_utilisateur) -> Utilisateur:
        """Trouver un utilisateur par son identifiant"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM utilisateur WHERE id_utilisateur = %(id_utilisateur)s;",
                        {"id_utilisateur": id_utilisateur},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if res:
            return Utilisateur(
                prenom=res["prenom"],
                nom=res["nom"],
                mdp=res["mdp"],
                naiss=res["naiss"],
                mail=res["mail"],
                id_utilisateur=res["id_utilisateur"],
            )
        return None

    @log
    def lister_tous(self) -> list[Utilisateur]:
        """Lister tous les utilisateurs"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM utilisateur;")
                    res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        utilisateurs = []
        for row in res:
            utilisateur = Utilisateur(
                id_utilisateur=row["id_utilisateur"],
                prenom=row["prenom"],
                nom=row["nom"],
                mdp=row["mdp"],
                naiss=row["naiss"],
                mail=row["mail"],
            )
            utilisateurs.append(utilisateur)
        return utilisateurs

    @log
    def modifier(self, utilisateur) -> bool:
        """Modifier un utilisateur dans la base de données"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE utilisateur SET "
                        "prenom = %(prenom)s, "
                        "nom = %(nom)s, "
                        "mdp = %(mdp)s, "
                        "naiss = %(naiss)s, "
                        "mail = %(mail)s "
                        "WHERE id_utilisateur = %(id_utilisateur)s;",
                        {
                            "prenom": utilisateur.prenom,
                            "nom": utilisateur.nom,
                            "mdp": utilisateur.mdp,
                            "naiss": utilisateur.naiss,
                            "mail": utilisateur.mail,
                            "id_utilisateur": utilisateur.id_utilisateur,
                        },
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
        return res == 1

    @log
    def supprimer(self, utilisateur) -> bool:
        """Supprimer un utilisateur de la base de données"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM utilisateur WHERE id_utilisateur = %(id_utilisateur)s;",
                        {"id_utilisateur": utilisateur.id_utilisateur},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise
        return res > 0

    @log
    def se_connecter(self, mail, mdp) -> Utilisateur:
        """Connexion d'un utilisateur avec mail et mot de passe"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM utilisateur "
                        "WHERE mail = %(mail)s AND mdp = %(mdp)s;",
                        {"mail": mail, "mdp": mdp},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            return None

        if res:
            return Utilisateur(
                id_utilisateur=res["id_utilisateur"],
                prenom=res["prenom"],
                nom=res["nom"],
                mdp=res["mdp"],
                naiss=res["naiss"],
                mail=res["mail"],
            )
        return None
