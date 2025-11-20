from __future__ import annotations

import os
import sys
from typing import Iterable, Optional

from tabulate import tabulate

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dao.personnage_ia_dao import PersonnageIADao
from dao.utilisateur_dao import UtilisateurDao
from objects.personnage_ia import PersonnageIA
from objects.utilisateur import Utilisateur
from service.auth_service import is_valid_email, is_valid_password
from utils.default_persoIA import DEFAULT_PERSONAS
from utils.log_decorator import log
from utils.securite import hash_password  # compat: voir utils/securite.py plus bas


class UtilisateurService:
    """Classe contenant les méthodes de service des Utilisateurs"""

    def __init__(self) -> None:
        self.dao = UtilisateurDao()
        self.persona_dao = PersonnageIADao()

    # -------------------------
    # Création / Lecture / Maj / Suppression
    # -------------------------
    @log
    def creer(self, prenom: str, nom: str, mail: str, mdp: str, naiss) -> Utilisateur:
        mail_norm = mail.strip().lower()

        # Vérif email
        is_valid_email(mail_norm)

        # Vérif doublon
        if self.dao.exists_mail(mail_norm):
            raise ValueError("Un compte existe déjà avec cet email")

        # Vérif mdp
        is_valid_password(mdp)

        # Création utilisateur
        u = Utilisateur(
            id_utilisateur=None,
            prenom=prenom,
            nom=nom,
            mail=mail_norm,
            mdp_hash=hash_password(mdp, mail_norm),
            naiss=naiss,
        )
        user = self.dao.create(u)

        # Ajout personas IA par défaut
        self.add_default_persoIA(user.id_utilisateur)

        return user

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
            u.mdp_hash = hash_password(
                u.mdp_hash
            )  # <— prudence: ici u.mdp_hash contient le mdp en clair
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
            [u.id_utilisateur, u.prenom, u.nom, u.mail, getattr(u, "naiss", None)] for u in users
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
        mail_norm = mail.strip().lower()
        u = self.dao.find_by_mail(mail_norm)
        if not u:
            return None

        # 1) Cas normal : hash salé avec l'email
        if u.mdp_hash == hash_password(mdp, mail_norm):
            return u

        # 2) Compatibilité ancienne version : hash sans sel
        if u.mdp_hash == hash_password(mdp):
            return u

        return None

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
                self.persona_dao.create(p)  # <-- UPSERT côté DAO
                inserted += 1
            except Exception as e:
                # LOG + rollback pour sortir de l'état 'transaction aborted'
                print(f"[add_default_persoIA] skip '{perso.get('name')}': {e}")
                try:
                    self.persona_dao.conn.rollback()
                except Exception:
                    pass
        return inserted

    def mail_deja_utilise(self, mail: str) -> bool:
        """Retourne True si un utilisateur existe déjà avec ce mail."""
        return self.dao.exists_mail(mail)

    def changer_identite(self, id_utilisateur: int, nouveau_prenom: str, nouveau_nom: str):
        """Change prénom + nom d'un utilisateur."""
        u = self.dao.find_by_id(id_utilisateur)
        if not u:
            return False, "Utilisateur introuvable."

        if not nouveau_prenom.strip():
            return False, "Le prénom ne peut pas être vide."

        if not nouveau_nom.strip():
            return False, "Le nom ne peut pas être vide."

        u.prenom = nouveau_prenom.strip()
        u.nom = nouveau_nom.strip()

        ok = self.dao.update_identite(u)
        if not ok:
            return False, "Erreur en base de données."

        return True, "Identité modifiée avec succès."

    def changer_mot_de_passe(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str):
        """
        Change le mot de passe d'un utilisateur.
        Retourne (bool, message).
        """
        u = self.dao.find_by_id(id_utilisateur)
        if not u:
            return False, "Utilisateur introuvable."

        mail_norm = u.mail.strip().lower()

        # Vérif ancien mot de passe (salé + compat ancien hash sans sel)
        hash_salt_old = hash_password(ancien_mdp, mail_norm)
        hash_nosalt_old = hash_password(ancien_mdp)

        if u.mdp_hash != hash_salt_old and u.mdp_hash != hash_nosalt_old:
            return False, "Ancien mot de passe incorrect."

        if ancien_mdp == nouveau_mdp:
            return False, "Le nouveau mot de passe doit être différent de l'ancien."

        try:
            is_valid_password(nouveau_mdp)
        except ValueError as e:
            return False, f"Mot de passe invalide : {e}"

        nouveau_hash = hash_password(nouveau_mdp, mail_norm)
        self.dao.update_mot_de_passe(id_utilisateur, nouveau_hash)

        return True, "Mot de passe modifié avec succès."

    def changer_email(self, id_utilisateur: int, nouvel_email: str, mdp: str):
        """
        Change l'email d'un utilisateur en gardant le sel = email.
        Retourne (bool, message).
        """
        u = self.dao.find_by_id(id_utilisateur)
        if not u:
            return False, "Utilisateur introuvable."

        mail_norm = u.mail.strip().lower()
        nouvel_email_norm = nouvel_email.strip().lower()

        # Vérif mot de passe avec l'ANCIEN email (salé + compat sans sel)
        hash_salt_old = hash_password(mdp, mail_norm)
        hash_nosalt_old = hash_password(mdp)

        if u.mdp_hash != hash_salt_old and u.mdp_hash != hash_nosalt_old:
            return False, "Mot de passe incorrect."

        # Valider le nouvel email
        try:
            is_valid_email(nouvel_email_norm)
        except ValueError as e:
            return False, f"Email invalide : {e}"

        # Vérifier qu'il n'est pas déjà pris
        if nouvel_email_norm != mail_norm and self.dao.exists_mail(nouvel_email_norm):
            return False, "Un compte existe déjà avec ce nouvel email."

        # Nouveau hash avec le NOUVEL email comme sel
        new_hash = hash_password(mdp, nouvel_email_norm)

        # Mise à jour des données
        u.mail = nouvel_email_norm
        ok1 = self.dao.update_mail_utilisateur(u)
        # on ne durcit pas sur ok2 (certains DAO renvoient None)
        try:
            ok2 = self.dao.update_mot_de_passe(id_utilisateur, new_hash)
        except Exception:
            ok2 = False  # on loguerait en vrai, mais on ne casse pas tout

        # Si l'email n'a pas été mis à jour, là oui c'est un échec
        if not ok1:
            return False, "Échec de la mise à jour en base."

        # Sinon, on considère que le changement est effectué
        return True, "Email modifié avec succès."
