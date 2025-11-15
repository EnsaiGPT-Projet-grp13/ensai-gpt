# tests/test_dao/test_utilisateur_dao.py

import uuid
from datetime import date

from dao.utilisateur_dao import UtilisateurDao
from objects.utilisateur import Utilisateur


def _make_fake_user(email_suffix: str = "") -> Utilisateur:
    """
    Fabrique un Utilisateur en mémoire, sans id, avec un email unique.
    On met un "hash" bidon dans mdp_hash, le DAO se contente de l'insérer tel quel.
    """
    unique_part = uuid.uuid4().hex[:8]
    mail = f"test_{unique_part}{email_suffix}@example.com"
    return Utilisateur(
        id_utilisateur=None,
        prenom="Test",
        nom="User",
        mail=mail,
        mdp_hash="HASH_INIT",
        naiss=date(2000, 1, 1),
    )


def test_create_and_find_by_id():
    """
    create(u) doit :
    - insérer l'utilisateur,
    - remplir u.id_utilisateur,
    - permettre de le relire avec find_by_id.
    """
    dao = UtilisateurDao()
    u = _make_fake_user()

    created = dao.create(u)

    # L'objet retourné doit avoir un id_utilisateur non nul
    assert created.id_utilisateur is not None

    # Vérification via find_by_id
    relu = dao.find_by_id(created.id_utilisateur)
    assert relu is not None
    assert relu.id_utilisateur == created.id_utilisateur
    assert relu.mail == created.mail
    assert relu.prenom == created.prenom
    assert relu.nom == created.nom

    # Nettoyage : suppression de l'utilisateur
    dao.delete(created.id_utilisateur)


def test_find_by_mail_retourne_utilisateur_si_existant():
    """
    find_by_mail(mail) doit renvoyer l'utilisateur correspondant quand il existe.
    """
    dao = UtilisateurDao()
    u = _make_fake_user()
    created = dao.create(u)

    relu = dao.find_by_mail(created.mail)

    assert relu is not None
    assert relu.id_utilisateur == created.id_utilisateur
    assert relu.mail == created.mail

    # Nettoyage
    dao.delete(created.id_utilisateur)


def test_find_by_mail_retourne_none_si_inexistant():
    """
    find_by_mail(mail) doit renvoyer None si aucun utilisateur ne correspond.
    """
    dao = UtilisateurDao()
    relu = dao.find_by_mail("does_not_exist_" + uuid.uuid4().hex + "@example.com")
    assert relu is None


def test_exists_mail_retourne_true_si_mail_existe():
    """
    exists_mail(mail) doit retourner True si le mail est présent en base.
    """
    dao = UtilisateurDao()
    u = _make_fake_user()
    created = dao.create(u)

    assert dao.exists_mail(created.mail) is True

    # Nettoyage
    dao.delete(created.id_utilisateur)


def test_exists_mail_retourne_false_si_mail_absent():
    """
    exists_mail(mail) doit retourner False pour un mail absent.
    """
    dao = UtilisateurDao()
    assert dao.exists_mail("absent_" + uuid.uuid4().hex + "@example.com") is False


def test_delete_supprime_vraiment_l_utilisateur():
    """
    delete(id) doit supprimer l'utilisateur, find_by_id doit ensuite renvoyer None.
    """
    dao = UtilisateurDao()
    u = _make_fake_user()
    created = dao.create(u)

    dao.delete(created.id_utilisateur)

    relu = dao.find_by_id(created.id_utilisateur)
    assert relu is None


def test_update_mot_de_passe_modifie_le_hash():
    """
    update_mot_de_passe(id, nouveau_hash) doit mettre à jour la colonne mdp.
    """
    dao = UtilisateurDao()
    u = _make_fake_user()
    created = dao.create(u)

    nouveau_hash = "NOUVEAU_HASH_TEST"
    dao.update_mot_de_passe(created.id_utilisateur, nouveau_hash)

    relu = dao.find_by_id(created.id_utilisateur)
    assert relu is not None
    assert relu.mdp_hash == nouveau_hash

    # Nettoyage
    dao.delete(created.id_utilisateur)
