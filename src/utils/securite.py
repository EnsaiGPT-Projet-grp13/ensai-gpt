# src/utils/securite.py
import hashlib

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def hash_password(pwd: str, salt: str | None = None) -> str:
    """
    Hash le mot de passe. Par défaut SANS sel (compatibilité avec la base existante).
    Tu peux activer un sel (par ex. email) à terme :
      hash_password(mdp, salt=mail)
    """
    if salt:
        return _sha256(pwd + ":" + salt)
    return _sha256(pwd)

# alias compat si le reste du code appelle encore hash_pwd
hash_pwd = hash_password
