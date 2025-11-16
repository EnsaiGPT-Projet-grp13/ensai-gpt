import pytest
from unittest.mock import patch

import requests

from service.conversation_service import ConversationService, _gen_token
from objects.conversation import Conversation
from objects.message import Message

class ReponseFactice:
    def __init__(self, json_data=None, text="", status_code=200, raise_json=False):
        self._json_data = json_data
        self.text = text
        self.status_code = status_code
        self._raise_json = raise_json

def test_start_cree_conversation_simple(service_conversation, personnage_factice):
    cree = {}

    class FausseConvDao:
        def create(self, conv: Conversation):
            conv.id_conversation = 10
            cree["conv"] = conv
            return conv

    service_conversation.conv_dao = FausseConvDao()

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
    class FausseConvDao:
        def create(self, conv: Conversation):
            conv.id_conversation = 11
            return conv

    service_conversation.conv_dao = FausseConvDao()

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

    class FausseConvDao:
        def find_by_token(self, token: str):
            assert token == "TOKEN123"
            return convo

        def add_participant(self, id_user: int, cid: int):
            appels.append((id_user, cid))

    service_conversation.conv_dao = FausseConvDao()

    conv = service_conversation.join_by_token(id_user=3, token="  token123  ")
    assert conv is convo
    assert appels == [(3, 7)]


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

    def json(self):
        if self._raise_json:
            raise ValueError("JSON invalide")
        return self._json_data




def test_extract_ai_text_depuis_resp_text():
    class R:
        text = "Salut"
        def json(self):
            raise ValueError("pas de JSON")
    resp = R()
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "Salut"

def test_extract_ai_text_depuis_chaine_simple():
    resp = ReponseFactice(
        json_data=ValueError("invalid json"),
        text="Bonjour !"
    )
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "Bonjour !"


def test_extract_ai_text_depuis_chaine_vide():
    resp = ReponseFactice(json_data="   ")
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "[IA] Réponse vide."


def test_extract_ai_text_retourne_placeholder_si_vide():
    resp = ReponseFactice(json_data="", text="")
    texte = ConversationService._extract_ai_text(resp)
    assert "[IA] Réponse vide." in texte

def test_ensure_conversation_ne_fait_rien_si_pas_d_utilisateur_ou_personnage(service_conversation, session_factice):
    s = session_factice
    service_conversation._ensure_conversation(s)
    assert s.conversation_id is None



def test_extract_ai_text_json_invalide_utilise_text():
    resp = ReponseFactice(json_data=ValueError("invalid json"), text="Réponse brute")
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "Réponse brute"
