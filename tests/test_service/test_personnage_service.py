import pytest
from unittest.mock import Mock

from service.personnage_service import PersonnageService
from objects.personnage_ia import PersonnageIA


@pytest.fixture
def service_personnage():
    return PersonnageService()


def test_lister_personnages_ia_pour_utilisateur_appelle_dao_avec_bon_id(service_personnage):
    dao_mock = Mock()
    dao_mock.lister_personnages_ia_pour_utilisateur.return_value = ["perso1", "perso2"]
    service_personnage.dao = dao_mock

    res = service_personnage.lister_personnages_ia_pour_utilisateur(42)

    assert res == ["perso1", "perso2"]
    dao_mock.lister_personnages_ia_pour_utilisateur.assert_called_once_with(42)


def test_list_standards_appelle_dao(service_personnage):
    dao_mock = Mock()
    dao_mock.list_standards.return_value = ["std1", "std2"]
    service_personnage.dao = dao_mock

    res = service_personnage.list_standards()

    assert res == ["std1", "std2"]
    dao_mock.list_standards.assert_called_once_with()


def test_lister_personnages_ia_crees_par_appelle_dao(service_personnage):
    dao_mock = Mock()
    dao_mock.lister_personnages_ia_crees_par.return_value = ["persoA", "persoB"]
    service_personnage.dao = dao_mock

    res = service_personnage.lister_personnages_ia_crees_par(10)

    assert res == ["persoA", "persoB"]
    dao_mock.lister_personnages_ia_crees_par.assert_called_once_with(10)


def test_get_by_id_retourne_personnage_si_trouve(service_personnage):
    perso = PersonnageIA(
        id_personnageIA=1,
        name="BotTest",
        system_prompt="Prompt test",
        created_by=None,
    )
    dao_mock = Mock()
    dao_mock.find_by_id.return_value = perso
    service_personnage.dao = dao_mock

    res = service_personnage.get_by_id(99)

    assert res is perso
    dao_mock.find_by_id.assert_called_once_with(99)


def test_get_by_id_retourne_none_si_inexistant(service_personnage):
    dao_mock = Mock()
    dao_mock.find_by_id.return_value = None
    service_personnage.dao = dao_mock

    res = service_personnage.get_by_id(1234)

    assert res is None
    dao_mock.find_by_id.assert_called_once_with(1234)


# =========================
# Tests de create_personnage
# =========================


def test_create_personnage_construit_objet_et_appelle_create(service_personnage):
    dao_mock = Mock()
    fake_perso = PersonnageIA(
        id_personnageIA=77,
        name="Mon Bot",
        system_prompt="Je suis un bot.",
        created_by=5,
    )
    dao_mock.create.return_value = fake_perso
    service_personnage.dao = dao_mock

    perso = service_personnage.create_personnage(
        uid=5,
        name="  Mon Bot  ",
        system_prompt="  Je suis un bot.  ",
    )

    assert perso is fake_perso
    dao_mock.create.assert_called_once()
    args, kwargs = dao_mock.create.call_args
    perso_cree = args[0]
    assert isinstance(perso_cree, PersonnageIA)
    assert perso_cree.name == "Mon Bot"
    assert perso_cree.system_prompt == "Je suis un bot."
    assert perso_cree.created_by == 5
    assert perso_cree.id_personnageIA is None


def test_update_personnage_retourne_none_si_id_inexistant(service_personnage):
    dao_mock = Mock()
    dao_mock.find_by_id.return_value = None
    service_personnage.dao = dao_mock

    res = service_personnage.update_personnage(
        pid=999,
        name="Nouveau nom",
        system_prompt="Nouveau prompt",
    )

    assert res is None
    dao_mock.find_by_id.assert_called_once_with(999)
    dao_mock.update.assert_not_called()


def test_update_personnage_modifie_nom_et_prompt(service_personnage):
    perso_initial = PersonnageIA(
        id_personnageIA=10,
        name="Ancien nom",
        system_prompt="Ancien prompt",
        created_by=3,
    )

    dao_mock = Mock()
    dao_mock.find_by_id.return_value = perso_initial
    dao_mock.update.return_value = perso_initial  # renvoyé après update
    service_personnage.dao = dao_mock

    res = service_personnage.update_personnage(
        pid=10,
        name=" Nouveau nom ",
        system_prompt=" Nouveau prompt ",
    )

    dao_mock.find_by_id.assert_called_once_with(10)
    dao_mock.update.assert_called_once_with(perso_initial)

    assert res is perso_initial
    assert res.name == "Nouveau nom"
    assert res.system_prompt == "Nouveau prompt"
    assert res.id_personnageIA == 10
    assert res.created_by == 3


def test_update_personnage_ne_change_rien_si_name_et_prompt_none(service_personnage):
    perso_initial = PersonnageIA(
        id_personnageIA=11,
        name="Nom fixe",
        system_prompt="Prompt fixe",
        created_by=1,
    )

    dao_mock = Mock()
    dao_mock.find_by_id.return_value = perso_initial
    dao_mock.update.return_value = perso_initial
    service_personnage.dao = dao_mock

    res = service_personnage.update_personnage(
        pid=11,
        name=None,
        system_prompt=None,
    )

    dao_mock.find_by_id.assert_called_once_with(11)
    dao_mock.update.assert_called_once_with(perso_initial)

    assert res.name == "Nom fixe"
    assert res.system_prompt == "Prompt fixe"


def test_update_personnage_ignore_nom_vide(service_personnage):
    perso_initial = PersonnageIA(
        id_personnageIA=12,
        name="Nom original",
        system_prompt="Prompt original",
        created_by=2,
    )

    dao_mock = Mock()
    dao_mock.find_by_id.return_value = perso_initial
    dao_mock.update.return_value = perso_initial
    service_personnage.dao = dao_mock

    res = service_personnage.update_personnage(
        pid=12,
        name="   ",  # nom vide
        system_prompt="Nouveau prompt",
    )

    assert res.name == "Nom original"
    assert res.system_prompt == "Nouveau prompt"
    dao_mock.update.assert_called_once_with(perso_initial)


def test_update_personnage_ignore_prompt_vide(service_personnage):
    perso_initial = PersonnageIA(
        id_personnageIA=13,
        name="Nom de base",
        system_prompt="Prompt de base",
        created_by=2,
    )

    dao_mock = Mock()
    dao_mock.find_by_id.return_value = perso_initial
    dao_mock.update.return_value = perso_initial
    service_personnage.dao = dao_mock

    res = service_personnage.update_personnage(
        pid=13,
        name="Nouveau nom",
        system_prompt="   ",  # prompt vide
    )

    assert res.name == "Nouveau nom"
    assert res.system_prompt == "Prompt de base"
    dao_mock.update.assert_called_once_with(perso_initial)


def test_delete_personnage_appelle_dao_delete(service_personnage):
    dao_mock = Mock()
    dao_mock.delete.return_value = True
    service_personnage.dao = dao_mock

    res = service_personnage.delete_personnage(50)

    assert res is True
    dao_mock.delete.assert_called_once_with(50)


def test_build_payload_avec_personnage_objet():
    perso = PersonnageIA(
        id_personnageIA=1,
        name="Bot",
        system_prompt="Tu es un bot.",
        created_by=None,
    )

    user_messages = [
        {"role": "user", "content": "Bonjour"},
        {"role": "assistant", "content": "Salut"},
    ]

    payload = PersonnageService.build_payload(
        personnage=perso,
        user_messages=user_messages,
    )

    assert "history" in payload
    assert payload["history"][0] == {"role": "system", "content": "Tu es un bot."}
    assert payload["history"][1:] == user_messages


def test_build_payload_avec_personnage_dict():
    perso_dict = {
        "id_personnageIA": 2,
        "name": "BotDict",
        "system_prompt": "Je viens d'un dict.",
    }

    user_messages = [
        {"role": "user", "content": "Question ?"},
    ]

    payload = PersonnageService.build_payload(
        personnage=perso_dict,
        user_messages=user_messages,
    )

    assert payload["history"][0] == {"role": "system", "content": "Je viens d'un dict."}
    assert payload["history"][1:] == user_messages
