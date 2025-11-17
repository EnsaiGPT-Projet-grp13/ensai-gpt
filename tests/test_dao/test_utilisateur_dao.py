import uuid

from dao.utilisateur_dao import UtilisateurDao
from tests.test_dao.helpers_dao import make_fake_user


def test_create_and_find_by_id():
    """
    create(u) doit insérer l'utilisateur, lui donner un id_utilisateur et find_by_id doit le retrouver
    """
    dao = UtilisateurDao()
    u = make_fake_user()

    created = dao.create(u)

    assert created.id_utilisateur is not None

    relu = dao.find_by_id(created.id_utilisateur)
    assert relu is not None
    assert relu.id_utilisateur == created.id_utilisateur
    assert relu.mail == created.mail
    assert relu.prenom == created.prenom
    assert relu.nom == created.nom

    dao.delete(created.id_utilisateur)


def test_find_by_mail_retourne_utilisateur_si_existant():
    dao = UtilisateurDao()
    u = make_fake_user()
    created = dao.create(u)

    relu = dao.find_by_mail(created.mail)

    assert relu is not None
    assert relu.id_utilisateur == created.id_utilisateur
    assert relu.mail == created.mail

    dao.delete(created.id_utilisateur)


def test_find_by_mail_retourne_none_si_inexistant():
    dao = UtilisateurDao()
    relu = dao.find_by_mail("does_not_exist_" + uuid.uuid4().hex + "@example.com")
    assert relu is None


def test_exists_mail_retourne_true_si_mail_existe():
    dao = UtilisateurDao()
    u = make_fake_user()
    created = dao.create(u)

    assert dao.exists_mail(created.mail) is True

    dao.delete(created.id_utilisateur)


def test_delete_supprime_vraiment_l_utilisateur():
    dao = UtilisateurDao()
    u = make_fake_user()
    created = dao.create(u)

    dao.delete(created.id_utilisateur)

    relu = dao.find_by_id(created.id_utilisateur)
    assert relu is None


def test_update_mot_de_passe_modifie_le_hash():
    dao = UtilisateurDao()
    u = make_fake_user()
    created = dao.create(u)

    nouveau_hash = "NOUVEAU_HASH_TEST"
    dao.update_mot_de_passe(created.id_utilisateur, nouveau_hash)

    relu = dao.find_by_id(created.id_utilisateur)
    assert relu is not None
    assert relu.mdp_hash == nouveau_hash

    dao.delete(created.id_utilisateur)
