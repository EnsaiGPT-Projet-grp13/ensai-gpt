# tests/test_service/test_auth_service.py

import pytest

from service.auth_service import AuthService, is_valid_email, is_valid_password


@pytest.fixture
def service_auth():
    """Instance d'AuthService pour les tests."""
    return AuthService()


# =========================
# Tests de validation email
# =========================

def test_email_valide_est_accepte():
    """is_valid_email ne doit pas lever d'erreur pour un email valide simple."""
    is_valid_email("user.test@example.com")


@pytest.mark.parametrize(
    "email",
    [
        "invalid",
        "user@",
        "@domain.com",
        "user@domain",
        "user@domain.",
        "user@.com",
        "user@@example.com",
    ],
)
def test_email_invalide_declenche_une_exception(email):
    """is_valid_email lève ValueError pour les emails invalides."""
    with pytest.raises(ValueError, match="Format email invalide"):
        is_valid_email(email)


def test_methode_static_is_valid_email_fonctionne_via_classe():
    """AuthService.is_valid_email doit accepter un email valide."""
    AuthService.is_valid_email("test.classe@example.com")


def test_methode_static_is_valid_email_fonctionne_via_instance(service_auth):
    """La méthode appelée sur l'instance doit se comporter comme la version statique."""
    service_auth.is_valid_email("test.instance@example.com")


# =========================
# Tests de validation mot de passe
# =========================

def test_mot_de_passe_solide_est_accepte():
    """is_valid_password ne doit pas lever d'erreur pour un mot de passe solide."""
    is_valid_password("Abcdef12")  # >= 8, maj, min, chiffre


def test_mot_de_passe_trop_court_declenche_une_exception():
    """Mot de passe < 8 caractères lève une ValueError."""
    with pytest.raises(ValueError, match="Au moins 8 caractères"):
        is_valid_password("Abc1")  # 4 caractères seulement


def test_mot_de_passe_sans_majuscule_declenche_une_exception():
    """Mot de passe sans majuscule lève ValueError."""
    with pytest.raises(ValueError, match="majuscule"):
        is_valid_password("abcdef12")  # pas de majuscule


def test_mot_de_passe_sans_minuscule_declenche_une_exception():
    """Mot de passe sans minuscule lève ValueError."""
    with pytest.raises(ValueError, match="minuscule"):
        is_valid_password("ABCDEF12")  # pas de minuscule


def test_mot_de_passe_sans_chiffre_declenche_une_exception():
    """Mot de passe sans chiffre -> ValueError."""
    with pytest.raises(ValueError, match="chiffre"):
        is_valid_password("Abcdefgh")  # pas de chiffre


def test_methode_static_is_valid_password_via_classe():
    """AuthService.is_valid_password doit fonctionner via la classe."""
    AuthService.is_valid_password("Abcdef12")


def test_methode_static_is_valid_password_via_instance(service_auth):
    """AuthService.is_valid_password doit fonctionner via l'instance."""
    service_auth.is_valid_password("Abcdef12")
