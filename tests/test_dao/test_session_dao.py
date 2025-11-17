from dao.utilisateur_dao import UtilisateurDao
from dao.session_dao import SessionDao

from tests.test_dao.helpers_dao import create_test_user


def test_open_cree_une_session_et_retourne_un_id():
    """open doit créer une session et retourner son id."""
    udao = UtilisateurDao()
    sdao = SessionDao()

    user = create_test_user(email_prefix="session_user")
    sid = sdao.open(user.id_utilisateur)

    assert sid is not None
    assert isinstance(sid, int)

    sessions = sdao.list_by_user(user.id_utilisateur, limit=10)
    ids = [s["id_session"] for s in sessions]
    assert sid in ids

    udao.delete(user.id_utilisateur)


def test_close_met_fin_a_la_session():
    """close doit renseigner ended_at et retourner True si la session était active"""
    udao = UtilisateurDao()
    sdao = SessionDao()

    user = create_test_user(email_prefix="session_close")
    sid = sdao.open(user.id_utilisateur)

    ok = sdao.close(sid)
    assert ok is True

    active = sdao.find_active_by_user(user.id_utilisateur)
    assert active is None

    udao.delete(user.id_utilisateur)


def test_find_active_by_user_retourne_derniere_session_non_terminee():
    """find_active_by_user doit retourner la dernière session ouverte non terminée."""
    udao = UtilisateurDao()
    sdao = SessionDao()

    user = create_test_user(email_prefix="session_active")

    sid1 = sdao.open(user.id_utilisateur)
    sdao.close(sid1)

    sid2 = sdao.open(user.id_utilisateur)

    active = sdao.find_active_by_user(user.id_utilisateur)
    assert active is not None
    assert active["id_session"] == sid2
    assert active["ended_at"] is None

    udao.delete(user.id_utilisateur)


def test_list_by_user_retourne_les_sessions_en_ordre_decroissant():
    """list_by_user doit retourner les sessions triées par started_at DESC."""
    udao = UtilisateurDao()
    sdao = SessionDao()

    user = create_test_user(email_prefix="session_list")

    sid1 = sdao.open(user.id_utilisateur)
    sid2 = sdao.open(user.id_utilisateur)

    sessions = sdao.list_by_user(user.id_utilisateur, limit=10)

    ids = [s["id_session"] for s in sessions]
    assert sid1 in ids
    assert sid2 in ids

    idx1 = ids.index(sid1)
    idx2 = ids.index(sid2)
    assert idx2 < idx1  # sid2 (plus récente) doit venir avant sid1

    udao.delete(user.id_utilisateur)
