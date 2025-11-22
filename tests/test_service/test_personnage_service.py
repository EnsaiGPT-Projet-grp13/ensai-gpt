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


