from __future__ import annotations
from typing import Optional, Iterable
from tabulate import tabulate

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.log_decorator import log
from utils.securite import hash_password  # compat: voir utils/securite.py plus bas

from objects.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
from utils.default_persoIA import DEFAULT_PERSONAS
from objects.personnage_ia import PersonnageIA
from dao.personnage_ia_dao import PersonnageIADao


class UtilisateurService:
    """Classe contenant les méthodes de service des Utilisateurs"""

    def __init__(self) -> None:
        self.dao = UtilisateurDao()
        self.persona_dao = PersonnageIADao()

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
        print("update réalisé")
        return True
    @log
    def changer_nom_utilisateur(self, uid: int, nouveau_nom: str) -> bool:
        """Permet à l'utilisateur connecté de changer son nom d'utilisateur."""
        try:
            # Trouver l'utilisateur existant
            utilisateur = self.dao.find_by_id(uid)
            if not utilisateur:
                raise ValueError("Utilisateur non trouvé.")
            
            # Modifier le nom de l'utilisateur
            utilisateur.nom_utilisateur = nouveau_nom

            # Appeler la méthode update du DAO pour mettre à jour l'utilisateur
            return self.dao.update_nom_utilisateur(utilisateur)# Appel de la méthode update du DAO

        except Exception as e:
            print(f"Erreur lors du changement de nom d'utilisateur : {repr(e)}")
            return False

    @log
    def changer_email(self, mail, nouvel_email):
        """Permet à l'utilisateur connecté de changer son nom d'utilisateur."""
        try:
            # Trouver l'utilisateur existant
            utilisateur = self.dao.find_by_mail(mail)
            if not utilisateur:
                raise ValueError("Utilisateur non trouvé.")
            
            # Modifier l'e-mail
            utilisateur.mail = nouvel_email

            # Appeler la méthode update du DAO pour mettre à jour l'utilisateur
            return self.dao.update_mail_utilisateur(utilisateur)# Appel de la méthode update du DAO

        except Exception as e:
            print(f"Erreur lors du changement de nom d'utilisateur : {repr(e)}")
            return False

    def add_default_persoIA(self, user_id: int):
        """Crée/Met à jour les personas par défaut pour un utilisateur."""
        inserted = 0
        for perso in DEFAULT_PERSONAS:
            try:
                p = PersonnageIA(
                    id_personnageIA=None,
                    name=perso["name"],
                    system_prompt=perso["system_prompt"],
                    created_by=user_id,
                )
                self.persona_dao.create(p)   # <-- UPSERT côté DAO
                inserted += 1
            except Exception as e:
                # LOG + rollback pour sortir de l'état 'transaction aborted'
                print(f"[add_default_persoIA] skip '{perso.get('name')}': {e}")
                try:
                    self.persona_dao.conn.rollback()
                except Exception:
                    pass
        return inserted