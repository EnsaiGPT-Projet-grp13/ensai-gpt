# tests/test_service/test_auth_service.py
import pytest
from datetime import date
from unittest.mock import Mock

from service.auth_service import (
    AuthService,
    is_valid_email,
    is_valid_password,
)
from dao.utilisateur_dao import UtilisateurDao


# =========================
# Tests des fonctions utilitaires
# =========================

def test_email_valide_est_accepte():
    """is_valid_email ne doit pas lever d'erreur pour un email valide simple."""
    is_valid_email("user.test@example.com")


@pytest.mark.parametrize("email", ["invalid", "user@", "@domain.com", "user@domain", "user@domain."])
def test_email_invalide_declenche_une_exception(email):
    """is_valid_email doit lever ValueError pour les emails invalides."""
    with pytest.raises(ValueError):
        is_valid_email(email)


def test_mot_de_passe_solide_est_accepte():
    """is_valid_password ne doit pas lever d'erreur pour un mot de passe fort."""
    is_valid_password("Abcdef12")


def test_mot_de_passe_trop_court_declenche_une_exception():
    """Mot de passe < 8 caractères -> ValueError."""
    with pytest.raises(ValueError, match="Au moins 8 caractères"):
        is_valid_password("Abc1")


def test_mot_de_passe_sans_majuscule_declenche_une_exception():
    """Mot de passe sans majuscule -> ValueError."""
    with pytest.raises(ValueError, match="majuscule"):
        is_valid_password("abcdef12")


def test_mot_de_passe_sans_minuscule_declenche_une_exception():
    """Mot de passe sans minuscule -> ValueError."""
    with pytest.raises(ValueError, match="minuscule"):
        is_valid_password("ABCDEF12")


def test_mot_de_passe_sans_chiffre_declenche_une_exception():
    """Mot de passe sans chiffre -> ValueError."""
    with pytest.raises(ValueError, match="chiffre"):
        is_valid_password("Abcdefgh")


# =========================
# Fixture spécifique AuthService
# =========================

@pytest.fixture
def service_auth():
    """Instance d'AuthService utilisée dans les tests."""
    return AuthService()


# =========================
# Tests de AuthService.find_user
# =========================

def test_find_user_retourne_utilisateur_si_mail_existe(service_auth, utilisateur_existant):
    """find_user doit retourner l'utilisateur quand le mail existe."""
    user = service_auth.find_user(utilisateur_existant.mail)
    assert user is not None
    assert user.id_utilisateur == utilisateur_existant.id_utilisateur
    assert user.mail == utilisateur_existant.mail


def test_find_user_retourne_none_si_mail_inconnu(service_auth):
    """find_user doit retourner None si l'email n'existe pas."""
    user = service_auth.find_user("doesnotexist@test.com")
    assert user is None


# =========================
# Tests de AuthService.check_password
# =========================

def test_check_password_retourne_true_si_mdp_correct(service_auth, utilisateur_existant):
    """check_password doit renvoyer True quand le mot de passe est correct."""
    assert service_auth.check_password(utilisateur_existant, "mdpAlice") is True


def test_check_password_retourne_false_si_mdp_incorrect(service_auth, utilisateur_existant):
    """check_password doit renvoyer False si le mot de passe est incorrect."""
    assert service_auth.check_password(utilisateur_existant, "MauvaisMotDePasse") is False


def test_check_password_normalise_bien_l_email(service_auth, utilisateur_existant):
    """
    Vérifie que la normalisation de l'email (strip + lower) est bien utilisée dans le hash.
    """
    user = utilisateur_existant
    user.mail = "  ALICE@TEST.com  "
    assert service_auth.check_password(user, "mdpAlice") is True


# =========================
# Tests de AuthService.se_connecter
# =========================

def test_se_connecter_retourne_utilisateur_si_identifiants_valides(service_auth, utilisateur_existant):
    """
    se_connecter doit renvoyer l'utilisateur quand email et mot de passe sont corrects.
    """
    user = service_auth.se_connecter(utilisateur_existant.mail, "mdpAlice")
    assert user is not None
    assert user.id_utilisateur == utilisateur_existant.id_utilisateur


def test_se_connecter_retourne_none_si_mdp_invalide(service_auth, utilisateur_existant):
    """se_connecter doit renvoyer None si le mot de passe est mauvais."""
    user = service_auth.se_connecter(utilisateur_existant.mail, "MauvaisMotDePasse")
    assert user is None


def test_se_connecter_retourne_none_si_mail_inconnu(service_auth):
    """se_connecter doit renvoyer None si l'email n'existe pas."""
    user = service_auth.se_connecter("unknown@test.com", "mdpInutile")
    assert user is None


# =========================
# Tests de AuthService.inscrire
# =========================

def test_inscrire_cree_utilisateur_en_base(service_auth):
    """
    inscrire doit :
    - normaliser l'email en minuscule
    - créer un utilisateur en base
    - retourner cet utilisateur avec un id non nul
    """
    dao = UtilisateurDao()
    mail = " NewUser@Test.com "
    prenom = "New"
    nom = "User"
    mdp = "Abcdef12"
    naiss = date(2000, 1, 1)

    mail_norm = mail.strip().lower()

    # Nettoyage préventif si le test a déjà tourné
    if dao.exists_mail(mail_norm):
        u_old = dao.find_by_mail(mail_norm)
        dao.delete(u_old.id_utilisateur)

    user = service_auth.inscrire(prenom, nom, mail, mdp, naiss)

    assert user.id_utilisateur is not None
    assert user.mail == mail_norm
    assert user.prenom == prenom
    assert user.nom == nom
    assert user.mdp_hash != mdp

    # Vérification en base via le DAO
    user_db = dao.find_by_mail(mail_norm)
    assert user_db is not None
    assert user_db.id_utilisateur == user.id_utilisateur


def test_inscrire_leve_exception_si_mail_deja_pris(service_auth, utilisateur_existant):
    """
    inscrire doit lever ValueError si un compte existe déjà avec cet email.
    """
    with pytest.raises(ValueError, match="Un compte existe déjà avec cet email"):
        service_auth.inscrire(
            prenom="Alice2",
            nom="Test2",
            mail=utilisateur_existant.mail,
            mdp="Abcdef12",
            naiss=date(2001, 1, 1),
        )


def test_inscrire_appelle_add_default_persoIA(service_auth):
    """
    Vérifie qu'inscrire appelle bien user_service.add_default_persoIA avec le bon id.
    """
    dao = UtilisateurDao()
    mail = "bob.persoia@test.com"
    if dao.exists_mail(mail):
        u = dao.find_by_mail(mail)
        dao.delete(u.id_utilisateur)

    faux_user_service = Mock()
    service_auth.user_service = faux_user_service

    user = service_auth.inscrire(
        prenom="Bob",
        nom="PersoIA",
        mail=mail,
        mdp="Abcdef12",
        naiss=date(1995, 5, 5),
    )

    faux_user_service.add_default_persoIA.assert_called_once_with(user.id_utilisateur)
