import re
from typing import Optional
from datetime import date
from dao.utilisateur_dao import UtilisateurDao
from utils.securite import hash_password
from objects.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService

def is_valid_email(email: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        raise ValueError("Format email invalide.")

def is_valid_password(pwd: str) -> None:
    if len(pwd) < 8:
        raise ValueError("Au moins 8 caractères requis.")
    if not re.search(r"[A-Z]", pwd):
        raise ValueError("Doit contenir une majuscule.")
    if not re.search(r"[a-z]", pwd):
        raise ValueError("Doit contenir une minuscule.")
    if not re.search(r"\d", pwd):
        raise ValueError("Doit contenir un chiffre.")


class AuthService:
    def __init__(self):
        self.dao = UtilisateurDao()
        self.user_service = UtilisateurService()

    # --- existant si tu veux le garder ---
    def se_connecter(self, mail: str, mdp: str) -> Optional[Utilisateur]:
        # normalisation de l'email
        mail_norm = (mail or "").strip().lower()

        # récupération de l'utilisateur avec l'email normalisé
        u = self.dao.find_by_mail(mail_norm)
        if not u:
            return None

        # comparaison avec le même schéma de hash que lors de l'inscription
        return u if u.mdp_hash == hash_password(mdp, mail_norm) else None
        

    # --- nouveaux helpers pour distinguer les cas ---
    def find_user(self, mail: str) -> Optional[Utilisateur]:
        return self.dao.find_by_mail(mail)

    def check_password(self, user, mdp: str) -> bool:
        # important: utiliser le même email normalisé que lors de l'insertion
        mail_norm = (user.mail or "").strip().lower()
        return user.mdp_hash == hash_password(mdp, mail_norm)


    def inscrire(self, prenom: str, nom: str, mail: str, mdp: str, naiss: date) -> Utilisateur:
        mail_norm = mail.strip().lower()
        if self.dao.exists_mail(mail_norm):
            raise ValueError("Un compte existe déjà avec cet email")

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

        # Ajout des personas IA par défaut
        self.user_service.add_default_persoIA(user.id_utilisateur)

        return user
