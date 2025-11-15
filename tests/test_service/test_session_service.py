# tests/test_service/test_session_service.py
import pytest

from service.session_service import SessionService


@pytest.fixture
def service_session():
    return SessionService()


# =========================
# Tests sur get_user_id
# =========================

def test_get_user_id_retourne_un_entier(service_session):
    service_session._s.utilisateur = {"id_utilisateur": "42"}
    uid = service_session.get_user_id()
    assert isinstance(uid, int)
    assert uid == 42


# =========================
# Tests sur set_personnage / get_personnage
# =========================

def test_set_personnage_enregistre_un_dict_correct(service_session):
    service_session.set_personnage(
        pid=3,
        name="BotTest",
        system_prompt="Tu es un bot de test.",
    )
    perso = service_session.get_personnage()
    assert isinstance(perso, dict)
    assert perso["id_personnageIA"] == 3
    assert perso["name"] == "BotTest"
    assert perso["system_prompt"] == "Tu es un bot de test."


def test_get_personnage_retourne_ce_qui_est_dans_la_session(service_session):
    """On vérifie que get_personnage retourne ce qui est stocké, même si présent par défaut."""
    perso = service_session.get_personnage()
    # On ne peut PAS supposer None -> on teste juste que ça renvoie ce que contient la session
    assert perso == service_session._s.personnage


# =========================
# Tests conversation
# =========================

def test_set_conversation_info_modifie_les_champs(service_session):
    service_session.set_conversation_info(
        cid=10,
        titre="Chat",
        is_collab=True,
        token="XYZ",
    )
    assert service_session.get_conversation_id() == 10
    assert service_session.get_conversation_title() == "Chat"
    assert service_session._s.conversation_is_collab is True
    assert service_session._s.conversation_token == "XYZ"


def test_get_conversation_id_retourne_valeur_stockee(service_session):
    """Même principe : Session possède déjà des valeurs. On vérifie la cohérence."""
    assert service_session.get_conversation_id() == service_session._s.conversation_id


def test_set_conversation_title_met_a_jour_uniquement_le_titre(service_session):
    service_session._s.conversation_id = 99
    service_session._s.conversation_title = "Ancien"
    service_session.set_conversation_title("Nouveau")

    assert service_session.get_conversation_id() == 99
    assert service_session.get_conversation_title() == "Nouveau"
