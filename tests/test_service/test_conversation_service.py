import pytest
from unittest.mock import Mock

from service.conversation_service import ConversationService
from objects.conversation import Conversation
from objects.message import Message


class ReponseFactice:
    def __init__(self, json_data, text=""):
        self._json_data = json_data
        self.text = text

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data
        return self._json_data


@pytest.fixture
def service_conversation():
    """
    Service de conversation avec DAO mockés pour éviter la vraie BDD.
    """
    service = ConversationService()
    service.conv_dao = Mock()
    service.msg_dao = Mock()
    return service


def test_start_cree_conversation_simple(service_conversation):
    """start doit construire une Conversation et appeler conv_dao.create une fois."""

    fake_conv_retour = Conversation(
        id_conversation=10,
        id_proprio=5,
        id_personnageIA=3,
        titre="Ma conversation",
        created_at=None,
        updated_at=None,
        temperature=None,
        top_p=None,
        max_tokens=150,
        is_collab=False,
        token_collab=None,
    )
    service_conversation.conv_dao.create.return_value = fake_conv_retour

    personnage = {
        "id_personnageIA": 3,
        "name": "BotTest",
        "system_prompt": "Prompt test",
    }

    conv = service_conversation.start(
        id_user=5,
        personnage=personnage,
        titre="Ma conversation",
    )

    service_conversation.conv_dao.create.assert_called_once()
    args, kwargs = service_conversation.conv_dao.create.call_args
    conv_passe = args[0]

    assert isinstance(conv_passe, Conversation)
    assert conv_passe.id_proprio == 5
    assert conv_passe.id_personnageIA == 3
    assert conv_passe.titre == "Ma conversation"
    assert conv_passe.max_tokens == 150
    assert conv_passe.is_collab is False
    assert conv_passe.token_collab is None

    assert conv is fake_conv_retour
    assert conv.id_conversation == 10




def test_join_by_token_retourne_none_si_token_vide(service_conversation):
    """join_by_token doit renvoyer None si le token est vide ou seulement des espaces."""
    res = service_conversation.join_by_token(id_user=5, token="   ")
    assert res is None
    service_conversation.conv_dao.find_by_token.assert_not_called()


def test_join_by_token_ajoute_participant_quand_token_valide(service_conversation):
    """
    join_by_token doit :
      - chercher la conversation via le token
      - appeler add_participant
      - renvoyer la conversation.
    """
    conv_factice = Conversation(
        id_conversation=42,
        id_proprio=1,
        id_personnageIA=3,
        titre="Conv collab",
        created_at=None,
        updated_at=None,
        temperature=None,
        top_p=None,
        max_tokens=150,
        is_collab=True,
        token_collab="ABCDEF1234567890",
    )

    service_conversation.conv_dao.find_by_token.return_value = conv_factice

    res = service_conversation.join_by_token(id_user=9, token="  abcdef1234567890  ")

    service_conversation.conv_dao.find_by_token.assert_called_once_with("ABCDEF1234567890")
    service_conversation.conv_dao.add_participant.assert_called_once_with(9, 42)
    assert res is conv_factice


def test_build_history_construit_system_et_messages(service_conversation):
    """build_history doit renvoyer l'historique au bon format, avec rôle system + messages."""
    # messages factices
    messages = [
        Message(
            id_message=1,
            id_conversation=10,
            expediteur="utilisateur",
            id_utilisateur=5,
            contenu="Bonjour",
        ),
        Message(
            id_message=2,
            id_conversation=10,
            expediteur="IA",
            id_utilisateur=None,
            contenu="Salut, comment puis-je t'aider ?",
        ),
    ]

    service_conversation.msg_dao.list_for_conversation.return_value = messages

    personnage = {
        "id_personnageIA": 3,
        "name": "BotTest",
        "system_prompt": "Tu es un bot de test.",
    }

    history = service_conversation.build_history(personnage, cid=10)

    # 1er message = system_prompt
    assert history[0] == {"role": "system", "content": "Tu es un bot de test."}
    # 2e message = utilisateur
    assert history[1]["role"] == "user"
    assert history[1]["content"] == "Bonjour"
    # 3e message = IA
    assert history[2]["role"] == "assistant"
    assert "comment puis-je t'aider" in history[2]["content"]

    service_conversation.msg_dao.list_for_conversation.assert_called_once_with(10)


def test_extract_ai_text_depuis_resp_text():
    """
    Cas où .json() renvoie directement une chaîne simple (format "ensaiGPT").
    """
    resp = ReponseFactice(json_data="Bonjour !")
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "Bonjour !"


def test_extract_ai_text_depuis_chaine_simple():
    """Si on passe directement une chaîne, elle est renvoyée telle quelle (trimée)."""
    texte = ConversationService._extract_ai_text("  Coucou  ")
    assert texte == "Coucou"


def test_extract_ai_text_depuis_chaine_vide():
    """Chaîne vide -> placeholder '[IA] Réponse vide.'."""
    texte = ConversationService._extract_ai_text("   ")
    assert texte == "[IA] Réponse vide."


def test_extract_ai_text_retourne_placeholder_si_vide():
    """Si rien n'est exploitable, on renvoie le placeholder."""
    resp = ReponseFactice(json_data="", text="")
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "[IA] Réponse vide."


def test_extract_ai_text_json_invalide_utilise_text():
    """
    Si resp.json() lève une exception, on utilise resp.text comme fallback.
    """
    resp = ReponseFactice(json_data=ValueError("invalid json"), text="Réponse brute")
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "Réponse brute"


def test_extract_ai_text_format_openai_like():
    """
    Cas d'un JSON de type OpenAI :
      {"choices": [{"message": {"content": "Texte IA"}}]}
    """
    resp = ReponseFactice(
        json_data={
            "choices": [
                {
                    "message": {"content": "Bonjour depuis OpenAI-like"},
                }
            ]
        }
    )
    texte = ConversationService._extract_ai_text(resp)
    assert texte == "Bonjour depuis OpenAI-like"


def test_extract_ai_text_detail_erreur():
    """
    Cas d'une réponse d'erreur de validation :
      {"detail": [{"msg": "..."}]}
    """
    resp = ReponseFactice(
        json_data={
            "detail": [
                {"msg": "Champ requis manquant"},
                {"msg": "Autre erreur"},
            ]
        }
    )
    texte = ConversationService._extract_ai_text(resp)
    assert texte.startswith("[API] ")
    assert "Champ requis manquant" in texte
    assert "Autre erreur" in texte

