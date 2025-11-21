import re


class AuthService:
    """
    Service d'authentification : validation des emails et des mots de passe.
    """

    @staticmethod
    def is_valid_password(pwd: str) -> None:
        """
        Valide un mot de passe.
        Lève ValueError si une des conditions n'est pas respectée.
        """
        if len(pwd) < 8:
            raise ValueError("Au moins 8 caractères requis.")
        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Doit contenir une majuscule.")
        if not re.search(r"[a-z]", pwd):
            raise ValueError("Doit contenir une minuscule.")
        if not re.search(r"\d", pwd):
            raise ValueError("Doit contenir un chiffre.")

    @staticmethod
    def is_valid_email(email: str) -> None:
        """
        Valide un email basique.
        Lève ValueError si le format est invalide.
        """
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            raise ValueError("Format email invalide.")


def is_valid_password(pwd: str) -> None:
    """Alias vers AuthService.is_valid_password."""
    return AuthService.is_valid_password(pwd)

def is_valid_email(email: str) -> None:
    """Alias vers AuthService.is_valid_email."""
    return AuthService.is_valid_email(email)
