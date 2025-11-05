from __future__ import annotations
from typing import Optional, Iterable
from tabulate import tabulate

from utils.log_decorator import log
from utils.securite import hash_password  # compat: voir utils/securite.py plus bas

from objects.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao


class UtilisateurService:
    """Classe contenant les méthodes de service des Utilisateurs"""

    def __init__(self) -> None:
        self.dao = UtilisateurDao()

    # -------------------------
    # Création / Lecture / Maj / Suppression
    # -------------------------
    @log
    def creer(self, prenom: str, nom: str, mail: str, mdp: str, naiss) -> Optional[Utilisateur]:
        """
        Création d'un utilisateur à partir de ses attributs.
        NOTE: on hash le mdp via hash_password(). Par défaut, SANS sel pour rester
        rétro-compatible avec les inserts existants (pop_db.py). Tu peux activer un sel (email)
        quand toute la base aura été migrée.
        """
        u = Utilisateur(
            id_utilisateur=None,
            prenom=prenom,
            nom=nom,
            mail=mail,
            mdp_hash=hash_password(mdp),  # <— pas de sel par défaut (compat)
            naiss=naiss,
        )
        ok = self.dao.create(u)
        return u if ok else None

    @log
    def lister_tous(self, inclure_mdp=False) -> list[Utilisateur]:
        """
        Liste tous les utilisateurs.
        Si inclure_mdp=False, on masque le hash pour l’affichage.
        """
        users = self.dao.lister_tous()
        if not inclure_mdp:
            for u in users:
                # on masque le hash en mémoire (affichage / retour)
                u.mdp_hash = None  # type: ignore[attr-defined]
        return users

    @log
    def trouver_par_id(self, id_utilisateur: int) -> Optional[Utilisateur]:
        """Trouver un utilisateur par son id."""
        return self.dao.find_by_id(id_utilisateur)

    @log
    def modifier(self, u: Utilisateur, *, rehash_password: bool = False) -> Optional[Utilisateur]:
        """
        Mettre à jour un utilisateur.
        Si rehash_password=True et que u.mdp_hash contient un MOT DE PASSE EN CLAIR,
        alors on le re-hash avant update (sinon on considère que mdp_hash est déjà un hash).
        """
        if rehash_password and u.mdp_hash:
            u.mdp_hash = hash_password(u.mdp_hash)  # <— prudence: ici u.mdp_hash contient le mdp en clair
        ok = self.dao.update(u)
        return u if ok else None

    @log
    def supprimer(self, u: Utilisateur) -> bool:
        """Supprimer un utilisateur."""
        return self.dao.delete(u.id_utilisateur)

    # -------------------------
    # Affichages & utilitaires
    # -------------------------
    @log
    def afficher_tous(self) -> str:
        """
        Affiche tous les utilisateurs (tableau).
        """
        entetes = ["id", "prenom", "nom", "mail", "naiss"]
        users = self.dao.lister_tous()
        # transforme en listes pour tabulate
        rows: Iterable[list] = (
            [u.id_utilisateur, u.prenom, u.nom, u.mail, getattr(u, "naiss", None)]
            for u in users
        )
        out = "-" * 100
        out += "\nListe des utilisateurs\n"
        out += "-" * 100 + "\n"
        out += tabulate(rows, headers=entetes, tablefmt="psql")
        out += "\n"
        return out

    # -------------------------
    # Connexion & vérifs
    # -------------------------
    @log
    def se_connecter(self, mail: str, mdp: str) -> Optional[Utilisateur]:
        """
        Se connecter à partir d'un mail et d'un mot de passe (en clair).
        Compare au hash stocké en BDD.
        NOTE: par défaut, hash sans sel pour rester compatible avec les données déjà insérées.
        Si tu souhaites durcir, passe à hash_password(mdp, salt=mail) ET réinsère/réhash toutes les données.
        """
        u = self.dao.find_by_mail(mail)
        if not u:
            return None
        return u if u.mdp_hash == hash_password(mdp) else None

    @log
    def mail_deja_utilise(self, mail: str) -> bool:
        """Retourne True si un utilisateur existe déjà avec ce mail."""
        return self.dao.exists_mail(mail)
        
    @log
    def changer_mot_de_passe(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str) -> bool:
        """
        Change le mot de passe d'un utilisateur :
        - Vérifie que l'ancien mot de passe est correct.
        - Hash le nouveau mot de passe et met à jour la BDD.
        Retourne True si tout s'est bien passé, False sinon.
        """
        u = self.dao.find_by_id(id_utilisateur)
        if not u:
            print("utilisateur introuvable")
            return False

        ancien_mdp_hash = hash_password(ancien_mdp, u.mail)

        if u.mdp_hash != ancien_mdp_hash:
            print("mdp differents")
            return False

        nouveau_hash = hash_password(nouveau_mdp, u.mail)

        self.dao.update_mot_de_passe(id_utilisateur, nouveau_hash)
        print("update réalisée")
        return True

        nouveau_hash = hash_password(nouveau_mdp)
        self.dao.update_mot_de_passe(id_utilisateur, nouveau_hash)
        print("update relaisee")
        return True

