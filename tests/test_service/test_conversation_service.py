# tests/test_service/test_conversation_service.py
import pytest
from unittest.mock import patch

import requests

from service.conversation_service import ConversationService, _gen_token
from objects.conversation import Conversation
from objects.message import Message


# =========================
# Tests sur _gen_token
# =========================

def test_gen_token_longueur_par_defaut():
    token = _gen_token()
    assert len(token) == 16


def test_gen_token_contient_uniquement_majuscules_et_chiffres():
    token = _gen_token(20)
    assert all(c.isupper() or c.isdigit() for c in token)


# =========================
# Tests de start()
# =========================

def test_start_cree_conversation_simple(service_conversation, personnage_factice):
    cree = {}

    class FauxConvDao:
        def create(self, conv: Conversation):
            conv.id_conversation = 10
            cree["conv"] = conv
            return conv

    service_conversation.conv_dao = FauxConvDao()

    conv = service_conversation.start(
        id_user=5,
        personnage={
            "id_personnageIA": personnage_factice.id_personnageIA,
            "name": personnage_factice.name,
            "system_prompt": personnage_factice.system_prompt,
        },
        titre="Test",
        temperature=None,
        top_p=None,
        max_tokens=None,
        is_collab=False,
    )

    assert conv.id_conversation == 10
    assert conv.id_proprio == 5
    assert conv.id_personnageIA == personnage_factice.id_personnageIA
    assert conv.max_tokens == 150
    assert conv.is_collab is False
    assert conv.token_collab is None


def test_start_conversation_collab_genere_un_token(service_conversation, personnage_factice):
    class FauxConvDao:
        def create(self, conv: Conversation):
            conv.id_conversation = 11
            return conv

    service_conversation.conv_dao = FauxConvDao()

    conv = service_conversation.start(
        id_user=2,
        personnage={
            "id_personnageIA": personnage_factice.id_personnageIA,
            "name": personnage_factice.name,
            "system_prompt": personnage_factice.system_prompt,
        },
        titre="Collab",
        is_collab=True,
        max_tokens=200,
        temperature=0.5,
        top_p=0.9,
    )

    assert conv.is_collab is True
    assert isinstance(conv.token_collab, str)
    assert len(conv.token_collab) == 16


# =========================
# Tests de join_by_token()
# =========================

def test_join_by_token_retourne_none_si_token_vide(service_conversation):
    conv = service_conversation.join_by_token(id_user=1, token="   ")
    assert conv is None


def test_join_by_token_ajoute_participant_quand_token_valide(service_conversation):
    convo = Conversation(
        id_conversation=7,
        id_proprio=1,
        id_personnageIA=2,
        titre="Collab",
        temperature=None,
        top_p=None,
        max_tokens=150,
        is_collab=True,
        token_collab="TOKEN123",
    )
    appels = []

    class FauxConvDao:
        def find_by_token(self, token: str):
            # On vérifie qu'on a bien normalisé le token
            assert token == "TOKEN123"
            return convo

        def add_participant(self, id_user: int, cid: int):
            appels.append((id_user, cid))

    service_conversation.conv_dao = FauxConvDao()

    conv = service_conversation.join_by_token(id_user=3, token="  token123  ")
    assert conv is convo
    assert appels == [(3, 7)]


# =========================
# Tests de build_history()
# =========================

def test_build_history_construit_system_et_messages(service_conversation, personnage_factice):
    messages = [
        Message(
            id_message=1,
            id_conversation=1,
            expediteur="utilisateur",
            id_utilisateur=5,
            contenu="Salut",
        ),
        Message(
            id_message=2,
            id_conversation=1,
            expediteur="IA",
            id_utilisateur=None,
            contenu="Bonjour, comment puis-je aider ?",
        ),
    ]

    class FauxMsgDao:
        def list_for_conversation(self, cid: int):
            assert cid == 1
            return messages

    service_conversation.msg_dao = FauxMsgDao()

    hist = service_conversation.build_history(
        {
            "system_prompt": personnage_factice.system_prompt
        },
        cid=1,
    )
    assert len(hist) == 3
    assert hist[0]["role"] == "system"
    assert hist[0]["content"] == personnage_factice.system_prompt
    assert hist[1]["role"] == "user"
    assert hist[2]["role"] == "assistant"


# =========================
# Tests de _make_payload()
# =========================

def test_make_payload_contient_champs_principaux(service_conversation, personnage_factice, monkeypatch):
    def faux_build_history(perso, cid):
        return [{"role": "system", "content": "test"}]

    monkeypatch.setattr(service_conversation, "build_history", faux_build_history)

    payload = service_conversation._make_payload(
        personnage={"system_prompt": personnage_factice.system_prompt},
        cid=1,
        temperature=0.7,
        top_p=0.9,
        max_tokens=100,
        stop=["STOP"],
    )

    assert payload["history"] == [{"role": "system", "content": "test"}]
    assert payload["max_tokens"] == 100
    assert payload["stop"] == ["STOP"]


# =========================
# Tests de _extract_ai_text()
# =========================

class ReponseFactice:
    def __init__(self, json_data=None, text="", status_code=200, raise_json=False):
        self._json_data = json_data
        self.text = text
        self.status_code = status_code
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise ValueError("JSON invalide")
        return self._json_data


def test_extract_ai_text_depuis_chaine_simple():
    resp = ReponseFactice(json_data="Bonjour !")
    texte = ConversationService._extract_ai_text(resp)  # type: ignore[arg-type]
    assert texte == "Bonjour !"


def test_extract_ai_text_depuis_format_openai_like():
    resp = ReponseFactice(json_data={
        "choices": [
            {"message": {"content": "Réponse IA"}}
        ]
    })
    texte = ConversationService._extract_ai_text(resp)  # type: ignore[arg-type]
    assert texte == "Réponse IA"


def test_extract_ai_text_retourne_placeholder_si_vide():
    resp = ReponseFactice(json_data="", text="")
    texte = ConversationService._extract_ai_text(resp)  # type: ignore[arg-type]
    assert "[IA] Réponse vide." in texte


# =========================
# Tests de send_user_and_get_ai()
# =========================

def test_send_user_and_get_ai_enregistre_messages_et_touche_conversation(
    service_conversation, personnage_factice, monkeypatch
):
    messages_ajoutes = []

    class FauxMsgDao:
        def add(self, msg: Message):
            messages_ajoutes.append(msg)

        def list_for_conversation(self, cid: int):
            return []

    class FauxConvDao:
        def __init__(self):
            self.last_touched = None

        def touch(self, cid: int):
            self.last_touched = cid

    service_conversation.msg_dao = FauxMsgDao()
    service_conversation.conv_dao = FauxConvDao()

    def faux_post(url, json, timeout):
        class R:
            status_code = 200
            def json(self_inner):
                return "Réponse IA de test"
        return R()

    monkeypatch.setattr("service.conversation_service.requests.post", faux_post)

    ia_text, payload = service_conversation.send_user_and_get_ai(
        cid=10,
        id_user=1,
        personnage={
            "system_prompt": personnage_factice.system_prompt
        },
        user_text="Bonjour !",
        temperature=0.7,
        top_p=0.9,
        max_tokens=50,
    )

    assert len(messages_ajoutes) == 2
    assert messages_ajoutes[0].expediteur == "utilisateur"
    assert messages_ajoutes[1].expediteur == "IA"
    assert ia_text == "Réponse IA de test"
    assert service_conversation.conv_dao.last_touched == 10


# =========================
# Tests de _ensure_conversation()
# =========================

def test_ensure_conversation_ne_fait_rien_si_pas_d_utilisateur_ou_personnage(service_conversation, session_factice):
    s = session_factice
    service_conversation._ensure_conversation(s)
    assert s.conversation_id is None


def test_ensure_conversation_cree_conversation_si_absente(
    service_conversation, session_factice, utilisateur_factice, personnage_factice
):
    s = session_factice
    s.utilisateur = utilisateur_factice
    s.personnage = personnage_factice
    s.conversation_title = "Titre test"
    s.conversation_is_collab = True

    class FauxConvDao:
        def create(self, conv: Conversation):
            assert conv.id_proprio == utilisateur_factice.id_utilisateur
            assert conv.id_personnageIA == personnage_factice.id_personnageIA
            assert conv.titre == "Titre test"
            conv.id_conversation = 99
            conv.is_collab = True
            conv.token_collab = "TOKEN123"
            return conv

    service_conversation.conv_dao = FauxConvDao()

    service_conversation._ensure_conversation(s)

    assert s.conversation_id == 99
    assert s.conversation_is_collab is True
    assert s.conversation_token == "TOKEN123"
    assert s.conversation_title is None
