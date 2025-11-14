import os
import pytest
from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.utilisateur_dao import UtilisateurDao
from objects.utilisateur import Utilisateur


def test_trouver_par_id_existant(utilisateur_existant):
    """Recherche par id d'un utilisateur existant"""
    # GIVEN
    id_utilisateur = utilisateur_existant.id_utilisateur

    # WHEN
    utilisateur = UtilisateurDao().trouver_par_id(id_utilisateur)

    # THEN
    assert utilisateur is not None
    assert utilisateur.id_utilisateur == id_utilisateur
    assert utilisateur.mail == "alice@test.io"


def test_trouver_par_id_non_existant():
    """Recherche par id d'un utilisateur n'existant pas"""
    # GIVEN
    id_inconnu = 999_999_999

    # WHEN
    utilisateur = UtilisateurDao().trouver_par_id(id_inconnu)

    # THEN
    assert utilisateur is None


def test_lister_tous():
    """Vérifie que la méthode renvoie une liste de Utilisateur de taille >= 0
    et que chaque élément est un Utilisateur.
    """
    # WHEN
    utilisateurs = UtilisateurDao().lister_tous()

    # THEN
    assert isinstance(utilisateurs, list)
    for u in utilisateurs:
        assert isinstance(u, Utilisateur)


def test_creer_ok():
    """Création d'Utilisateur réussie"""
    # GIVEN
    u = Utilisateur(
        prenom="Bob",
        nom="Essai",
        mdp=hash_password("bobpwd", "bob@exemple.com"),
        naiss="2001-02-02",
        mail="bob@exemple.com",
    )

    # WHEN
    creation_ok = UtilisateurDao().creer(u)

    # THEN
    assert creation_ok
    assert u.id_utilisateur


def test_creer_ko():
    """Création d'Utilisateur échouée (données invalide)"""
    # GIVEN (naiss invalide + mail non string)
    u = Utilisateur(
        prenom="Bad",
        nom="Data",
        mdp="enclair",          # même si en clair, l'échec vient d'autres champs
        naiss="date_invalide",  # devrait être 'YYYY-MM-DD'
        mail=12345,             # devrait être une chaîne
    )

    # WHEN
    creation_ok = UtilisateurDao().creer(u)

    # THEN
    assert not creation_ok


def test_modifier_ok(utilisateur_existant):
    """Modification d'Utilisateur réussie"""
    # GIVEN
    utilisateur_existant.nom = "Modifie"
    utilisateur_existant.mdp = "nouveau_mdp_en_clair"
    # La DAO/service re-hash généralement côté service, mais ici on hash pour tester la DAO seule
    utilisateur_existant.mdp = hash_password(
        utilisateur_existant.mdp, utilisateur_existant.mail
    )

    # WHEN
    modification_ok = UtilisateurDao().modifier(utilisateur_existant)

    # THEN
    assert modification_ok

    # Et on peut revérifier en rechargant
    reloaded = UtilisateurDao().trouver_par_id(utilisateur_existant.id_utilisateur)
    assert reloaded.nom == "Modifie"


def test_modifier_ko():
    """Modification d'Utilisateur échouée (id inconnu)"""
    # GIVEN
    u = Utilisateur(
        id_utilisateur=888888,
        prenom="Id",
        nom="Inconnu",
        mdp=hash_password("x", "id.inconnu@z.fr"),
        naiss="1999-09-09",
        mail="id.inconnu@z.fr",
    )

    # WHEN
    modification_ok = UtilisateurDao().modifier(u)

    # THEN
    assert not modification_ok


def test_supprimer_ok(utilisateur_existant):
    """Suppression d'Utilisateur réussie"""
    # GIVEN: on supprime l'utilisateur créé par le fixture
    # WHEN
    suppression_ok = UtilisateurDao().supprimer(utilisateur_existant)

    # THEN
    assert suppression_ok
    # Et vérifier qu'il n'existe plus
    assert UtilisateurDao().trouver_par_id(utilisateur_existant.id_utilisateur) is None


def test_supprimer_ko():
    """Suppression d'Utilisateur échouée (id inconnu)"""
    # GIVEN
    u = Utilisateur(
        id_utilisateur=777777,
        prenom="No",
        nom="Body",
        mdp=hash_password("nop", "nobody@z.fr"),
        naiss="1990-10-10",
        mail="nobody@z.fr",
    )

    # WHEN
    suppression_ok = UtilisateurDao().supprimer(u)

    # THEN
    assert not suppression_ok


def test_se_connecter_ok():
    """Connexion d'Utilisateur réussie (mail + mdp)"""
    # GIVEN: on crée un utilisateur puis on tente la connexion
    mail = "login@test.io"
    mdp_clair = "1234"
    u = Utilisateur(
        prenom="Login",
        nom="Ok",
        mdp=hash_password(mdp_clair, mail),
        naiss="2002-03-04",
        mail=mail,
    )
    assert UtilisateurDao().creer(u)

    # WHEN
    utilisateur = UtilisateurDao().se_connecter(mail, hash_password(mdp_clair, mail))

    # THEN
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.mail == mail


def test_se_connecter_ko():
    """Connexion d'Utilisateur échouée (mail ou mdp incorrect)"""
    # GIVEN
    mail = "unk@now.n"
    mdp = "wrong"

    # WHEN
    utilisateur = UtilisateurDao().se_connecter(mail, hash_password(mdp, mail))

    # THEN
    assert utilisateur is None


if __name__ == "__main__":
    pytest.main([__file__])
