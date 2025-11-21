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
from utils.securite import hash_password


class UtilisateurService:
    """Classe contenant les méthodes de service des Utilisateurs"""

    def __init__(self) -> None:
        self.dao = UtilisateurDao()
        self.persona_dao = PersonnageIADao()

    @log
    def creer(self, prenom: str, nom: str, mail: str, mdp: str, naiss) -> Utilisateur:
        mail_norm = mail.strip().lower()

        is_valid_email(mail_norm)

        if self.dao.exists_mail(mail_norm):
            raise ValueError("Un compte existe déjà avec cet email")

        is_valid_password(mdp)

        u = Utilisateur(
            id_utilisateur=None,
            prenom=prenom,
            nom=nom,
            mail=mail_norm,
            mdp_hash=hash_password(mdp, mail_norm),
            naiss=naiss,
        )
        user = self.dao.create(u)

        self.add_default_persoIA(user.id_utilisateur)

        return user

    @log
    def trouver_par_id(self, id_utilisateur: int) -> Optional[Utilisateur]:
        """Trouver un utilisateur par son id."""
        return self.dao.find_by_id(id_utilisateur)

    @log
    def supprimer(self, u: Utilisateur) -> bool:
        """Supprimer un utilisateur."""
        return self.dao.delete(u.id_utilisateur)
        # focntionnalite future : supprimer son compte utilisateur

    @log
    def se_connecter(self, mail: str, mdp: str) -> Optional[Utilisateur]:
        mail_norm = mail.strip().lower()
        u = self.dao.find_by_mail(mail_norm)
        if not u:
            return None
        if u.mdp_hash == hash_password(mdp, mail_norm):
            return u
        return None

    def add_default_persoIA(self, user_id: int):
        """Crée les personas par défaut pour un utilisateur."""
        inserted = 0
        for perso in DEFAULT_PERSONAS:
            try:
                p = PersonnageIA(
                    id_personnageIA=None,
                    name=perso["name"],
                    system_prompt=perso["system_prompt"],
                    created_by=user_id,
                )
                self.persona_dao.create(p)
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

    def changer_identite(
        self, id_utilisateur: int, nouveau_prenom: str, nouveau_nom: str
    ):
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

    def changer_mot_de_passe(
        self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str
    ):
        """
        Change le mot de passe d'un utilisateur.
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

        try:
            is_valid_email(nouvel_email_norm)
        except ValueError as e:
            return False, f"Email invalide : {e}"

        if nouvel_email_norm != mail_norm and self.dao.exists_mail(nouvel_email_norm):
            return False, "Un compte existe déjà avec ce nouvel email."

        # Nouveau hash avec le NOUVEL email comme sel
        new_hash = hash_password(mdp, nouvel_email_norm)

        u.mail = nouvel_email_norm
        ok1 = self.dao.update_mail_utilisateur(u)

        try:
            ok2 = self.dao.update_mot_de_passe(id_utilisateur, new_hash)
        except Exception:
            ok2 = False

        if not ok1:
            return False, "Échec de la mise à jour en base."
        return True, "Email modifié avec succès."
