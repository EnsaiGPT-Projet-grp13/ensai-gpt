# tests/test_dao/test_session_dao.py

import uuid
from datetime import date

from dao.utilisateur_dao import UtilisateurDao
from dao.session_dao import SessionDao
from objects.utilisateur import Utilisateur


def _create_user() -> Utilisateur:
    """Crée un utilisateur de test en base et le retourne."""
    udao = UtilisateurDao()
    mail = f"session_user_{uuid.uuid4().hex[:8]}@example.com"
    u = Utilisateur(
        id_utilisateur=None,
        prenom="Sess",
        nom="User",
        mail=mail,
        mdp_hash="HASH_TEST",
        naiss=date(2000, 1, 1),
    )
    return udao.create(u)


def test_open_cree_une_session_et_retourne_un_id():
    """open doit créer une session et retourner son id."""
    udao = UtilisateurDao()
    sdao = SessionDao()

    user = _create_user()
    sid = sdao.open(user.id_utilisateur)

    assert sid is not None
    assert isinstance(sid, int)

    # Vérifie qu'elle apparaît bien dans list_by_user
    sessions = sdao.list_by_user(user.id_utilisateur, limit=10)
    ids = [s["id_session"] for s in sessions]
    assert sid in ids

    # Nettoyage
    udao.delete(user.id_utilisateur)


def test_close_met_fin_a_la_session():
    """close doit renseigner ended_at et retourner True si la session était active."""
    udao = UtilisateurDao()
    sdao = SessionDao()

    user = _create_user()
    sid = sdao.open(user.id_utilisateur)

    ok = sdao.close(sid)
    assert ok is True

    # La session ne doit plus être considérée comme active
    active = sdao.find_active_by_user(user.id_utilisateur)
    assert active is None

    udao.delete(user.id_utilisateur)


def test_find_active_by_user_retourne_derniere_session_non_terminee():
    """
    find_active_by_user doit retourner la dernière session ouverte
    dont ended_at est NULL.
    """
    udao = UtilisateurDao()
    sdao = SessionDao()

    user = _create_user()

    # Première session, qu'on ferme
    sid1 = sdao.open(user.id_utilisateur)
    sdao.close(sid1)

    # Deuxième session, laissée ouverte
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

    user = _create_user()

    sid1 = sdao.open(user.id_utilisateur)
    sid2 = sdao.open(user.id_utilisateur)

    sessions = sdao.list_by_user(user.id_utilisateur, limit=10)

    # On doit avoir au moins les 2 sessions
    ids = [s["id_session"] for s in sessions]
    assert sid1 in ids
    assert sid2 in ids

    # Et la dernière ouverte (sid2) doit apparaître avant la première (sid1)
    idx1 = ids.index(sid1)
    idx2 = ids.index(sid2)
    assert idx2 < idx1  # ordre décroissant sur started_at

    udao.delete(user.id_utilisateur)
