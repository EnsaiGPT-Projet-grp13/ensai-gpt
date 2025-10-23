from typing import Optional
from datetime import date
from dao.utilisateur_dao import UtilisateurDao
from utils.securite import hash_pwd
from objects.utilisateur import Utilisateur


class AuthService:
    def __init__(self):
        self.dao = UtilisateurDao()

    # --- existant si tu veux le garder ---
    def se_connecter(self, mail: str, mdp: str) -> Optional[Utilisateur]:
        u = self.dao.find_by_mail(mail)
        if not u:
            return None
        return u if u.mdp_hash == hash_pwd(mdp) else None

    # --- nouveaux helpers pour distinguer les cas ---
    def find_user(self, mail: str) -> Optional[Utilisateur]:
        return self.dao.find_by_mail(mail)

    def check_password(self, user, mdp: str) -> bool:
        # important: utiliser le même email normalisé que lors de l'insertion
        mail_norm = (user.mail or "").strip().lower()
        return user.mdp_hash == hash_pwd(mdp, mail_norm)


    def inscrire(self, prenom: str, nom: str, mail: str, mdp: str, naiss: date) -> Utilisateur:
        if "@" not in mail:
            raise ValueError("Email invalide")
        if self.dao.exists_mail(mail):
            raise ValueError("Un compte existe déjà avec cet email")
        mail_norm = mail.strip().lower()
        u = Utilisateur(
            id_utilisateur=None,
            prenom=prenom, nom=nom, mail=mail,
            mdp_hash = hash_pwd(mdp, mail_norm),
            naiss=naiss,
        )
        return self.dao.create(u)
