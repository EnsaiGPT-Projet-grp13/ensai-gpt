import hashlib


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hash_password(pwd: str, sel: str | None = None) -> str:
    """
    Hash le mot de passe. Par défaut SANS sel (compatibilité avec la base existante).
    Tu peux activer un sel (par ex. email) à terme :
      hash_password(mdp, sel=mail)
    """
    if sel:
        return _sha256(pwd + ":" + sel)
    return _sha256(pwd)
