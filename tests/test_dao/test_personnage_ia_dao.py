from dao.utilisateur_dao import UtilisateurDao
from dao.personnage_ia_dao import PersonnageIADao
from objects.personnage_ia import PersonnageIA

from tests.test_dao.helpers_dao import (
    create_test_user,
    create_test_personnage,
    create_standard_personnage,
)


def test_create_and_find_by_id_personnage():
    """
    create(p) doit insérer un personnage IA et find_by_id(pid) doit le retrouver.
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()
    user = create_test_user(email_prefix="perso_user")
    created = create_test_personnage(user.id_utilisateur, prefix="BotTest")

    assert created.id_personnageIA is not None
    assert created.created_by == user.id_utilisateur

    # 3) vérifier via find_by_id
    relu = pdao.find_by_id(created.id_personnageIA)
    assert relu is not None
    assert relu.id_personnageIA == created.id_personnageIA
    assert relu.name == created.name
    assert relu.system_prompt == created.system_prompt

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

    user = create_test_user(email_prefix="perso_upsert")
    name = "BotUpsertTest"

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

    pdao.delete(created1.id_personnageIA)
    udao.delete(user.id_utilisateur)


def test_delete_retourne_true_quand_un_personnage_est_supprime():
    """
    delete(pid) doit retourner True quand une ligne est effectivement supprimée,
    et False si rien n'est supprimé.
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()

    user = create_test_user(email_prefix="perso_delete")
    created = create_test_personnage(user.id_utilisateur, prefix="BotDelete")

    # 1er delete -> True
    ok = pdao.delete(created.id_personnageIA)
    assert ok is True

    # 2e delete sur le même id -> False
    ok2 = pdao.delete(created.id_personnageIA)
    assert ok2 is False

    udao.delete(user.id_utilisateur)


def test_lister_personnages_ia_crees_par_ne_retourne_que_les_personnages_de_ce_user():
    """
    lister_personnages_ia_crees_par(uid) doit lister uniquement les personnages créés par cet utilisateur.
    """
    udao = UtilisateurDao()
    pdao = PersonnageIADao()

    user1 = create_test_user(email_prefix="perso_user1")
    user2 = create_test_user(email_prefix="perso_user2")

    p1 = create_test_personnage(user1.id_utilisateur, prefix="BotUser1")
    p2 = create_test_personnage(user2.id_utilisateur, prefix="BotUser2")

    liste1 = pdao.lister_personnages_ia_crees_par(user1.id_utilisateur)
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

