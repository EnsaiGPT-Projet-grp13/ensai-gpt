# tests/test_dao/test_personnage_ia_dao.py

import uuid
from datetime import date

from dao.utilisateur_dao import UtilisateurDao
from dao.personnage_ia_dao import PersonnageIADao
from objects.utilisateur import Utilisateur
from objects.personnage_ia import PersonnageIA


def _make_fake_user() -> Utilisateur:
    """
    Crée un utilisateur factice avec un email unique, sans id.
    Utilisé pour les tests de PersonnageIADao.
    """
    unique_part = uuid.uuid4().hex[:8]
    mail = f"perso_user_{unique_part}@example.com"
    return Utilisateur(
        id_utilisateur=None,
        prenom="Perso",
        nom="Owner",
        mail=mail,
        mdp_hash="HASH_TEST",
        naiss=date(2000, 1, 1),
    )


def _create_user_in_db() -> Utilisateur:
    """Insère un utilisateur en base et le retourne avec son id_utilisateur renseigné."""
    udao = UtilisateurDao()
    u = _make_fake_user()
    created = udao.create(u)
    return created


def test_create_and_find_by_id_personnage():
    """
    create(p) doit insérer un personnage IA et find_by_id(pid) doit le retrouver.
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()

    # 1) créer un utilisateur propriétaire
    user = _create_user_in_db()

    # 2) créer un personnage IA
    p = PersonnageIA(
        id_personnageIA=None,
        name="BotTest_" + uuid.uuid4().hex[:6],
        system_prompt="Je suis un bot de test.",
        created_by=user.id_utilisateur,
    )
    created = pdao.create(p)

    assert created.id_personnageIA is not None
    assert created.name == p.name
    assert created.created_by == user.id_utilisateur

    # 3) vérifier via find_by_id
    relu = pdao.find_by_id(created.id_personnageIA)
    assert relu is not None
    assert relu.id_personnageIA == created.id_personnageIA
    assert relu.name == created.name
    assert relu.system_prompt == created.system_prompt

    # Nettoyage
    pdao.delete(created.id_personnageIA)
    udao.delete(user.id_utilisateur)


def test_create_fait_un_upsert_sur_name_et_created_by():
    """
    create(p) doit faire un UPSERT sur (name, created_by) :
    - 1er appel : insert
    - 2e appel avec même (name, created_by) et prompt différent : update
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()

    user = _create_user_in_db()
    name = "BotUpsert_" + uuid.uuid4().hex[:6]

    p1 = PersonnageIA(
        id_personnageIA=None,
        name=name,
        system_prompt="Prompt v1",
        created_by=user.id_utilisateur,
    )
    created1 = pdao.create(p1)

    p2 = PersonnageIA(
        id_personnageIA=None,
        name=name,
        system_prompt="Prompt v2",
        created_by=user.id_utilisateur,
    )
    created2 = pdao.create(p2)

    # Même id (update) et prompt mis à jour
    assert created2.id_personnageIA == created1.id_personnageIA
    assert created2.system_prompt == "Prompt v2"

    # Nettoyage
    pdao.delete(created1.id_personnageIA)
    udao.delete(user.id_utilisateur)


def test_delete_retourne_true_quand_un_personnage_est_supprime():
    """
    delete(pid) doit retourner True quand une ligne est effectivement supprimée,
    et False si rien n'est supprimé.
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()

    user = _create_user_in_db()

    p = PersonnageIA(
        id_personnageIA=None,
        name="BotDelete_" + uuid.uuid4().hex[:6],
        system_prompt="À supprimer.",
        created_by=user.id_utilisateur,
    )
    created = pdao.create(p)

    # 1er delete -> True
    ok = pdao.delete(created.id_personnageIA)
    assert ok is True

    # 2e delete sur le même id -> False
    ok2 = pdao.delete(created.id_personnageIA)
    assert ok2 is False

    # Nettoyage
    udao.delete(user.id_utilisateur)


def test_list_by_creator_ne_retourne_que_les_personnages_de_ce_user():
    """
    list_by_creator(uid) doit lister uniquement les personnages créés par cet utilisateur.
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()

    user1 = _create_user_in_db()
    user2 = _create_user_in_db()

    p1 = pdao.create(
        PersonnageIA(
            id_personnageIA=None,
            name="BotUser1_" + uuid.uuid4().hex[:4],
            system_prompt="Pour user1",
            created_by=user1.id_utilisateur,
        )
    )
    p2 = pdao.create(
        PersonnageIA(
            id_personnageIA=None,
            name="BotUser2_" + uuid.uuid4().hex[:4],
            system_prompt="Pour user2",
            created_by=user2.id_utilisateur,
        )
    )

    liste1 = pdao.list_by_creator(user1.id_utilisateur)
    noms1 = {p.name for p in liste1}
    creators1 = {p.created_by for p in liste1}

    assert p1.name in noms1
    assert p2.name not in noms1
    assert creators1 == {user1.id_utilisateur}

    # Nettoyage
    pdao.delete(p1.id_personnageIA)
    pdao.delete(p2.id_personnageIA)
    udao.delete(user1.id_utilisateur)
    udao.delete(user2.id_utilisateur)


def test_list_standards_inclut_les_personnages_sans_created_by():
    """
    list_standards() doit retourner les personnages avec created_by IS NULL.
    On en crée un pour être sûrs qu'il est présent.
    """
    pdao = PersonnageIADao()

    # Création d'un personnage standard (created_by = None)
    p_std = PersonnageIA(
        id_personnageIA=None,
        name="StandardTest_" + uuid.uuid4().hex[:4],
        system_prompt="Standard de test.",
        created_by=None,
    )
    created_std = pdao.create(p_std)

    standards = pdao.list_standards()
    ids = {p.id_personnageIA for p in standards}

    assert created_std.id_personnageIA in ids

    # Nettoyage
    pdao.delete(created_std.id_personnageIA)


def test_list_for_user_retourne_standards_et_personnages_de_l_utilisateur():
    """
    list_for_user(uid) doit retourner :
    - les personnages standards (created_by IS NULL)
    - les personnages créés par l'utilisateur uid
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()

    user = _create_user_in_db()

    # 1) standard
    p_std = pdao.create(
        PersonnageIA(
            id_personnageIA=None,
            name="StdListForUser_" + uuid.uuid4().hex[:4],
            system_prompt="Standard pour list_for_user.",
            created_by=None,
        )
    )

    # 2) perso du user
    p_user = pdao.create(
        PersonnageIA(
            id_personnageIA=None,
            name="UserListForUser_" + uuid.uuid4().hex[:4],
            system_prompt="Perso user.",
            created_by=user.id_utilisateur,
        )
    )

    liste = pdao.list_for_user(user.id_utilisateur)
    ids = {p.id_personnageIA for p in liste}
    creators = {p.created_by for p in liste}

    # On s'assure que nos deux persos sont dedans
    assert p_std.id_personnageIA in ids
    assert p_user.id_personnageIA in ids

    # created_by contient au moins {None, user.id}
    assert None in creators
    assert user.id_utilisateur in creators

    # Nettoyage
    pdao.delete(p_std.id_personnageIA)
    pdao.delete(p_user.id_personnageIA)
    udao.delete(user.id_utilisateur)
