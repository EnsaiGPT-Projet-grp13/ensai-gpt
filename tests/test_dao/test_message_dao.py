# tests/test_dao/test_message_dao.py

import uuid
from datetime import date

from dao.utilisateur_dao import UtilisateurDao
from dao.personnage_ia_dao import PersonnageIADao
from dao.conversation_dao import ConversationDao
from dao.message_dao import MessageDao

from objects.utilisateur import Utilisateur
from objects.personnage_ia import PersonnageIA
from objects.conversation import Conversation
from objects.message import Message


def _create_user() -> Utilisateur:
    """Insère un utilisateur de test en base et le retourne."""
    udao = UtilisateurDao()
    mail = f"msg_user_{uuid.uuid4().hex[:8]}@example.com"
    u = Utilisateur(
        id_utilisateur=None,
        prenom="Msg",
        nom="User",
        mail=mail,
        mdp_hash="HASH_TEST",
        naiss=date(2000, 1, 1),
    )
    return udao.create(u)


def _create_personnage(owner_id: int) -> PersonnageIA:
    """Crée un personnage IA pour un utilisateur donné."""
    pdao = PersonnageIADao()
    p = PersonnageIA(
        id_personnageIA=None,
        name="BotMsg_" + uuid.uuid4().hex[:4],
        system_prompt="Bot pour tests de messages.",
        created_by=owner_id,
    )
    return pdao.create(p)


def _create_conversation(owner_id: int, pid: int) -> Conversation:
    """Crée une conversation simple pour un utilisateur et un personnage."""
    cdao = ConversationDao()
    c = Conversation(
        id_conversation=None,
        id_proprio=owner_id,
        id_personnageIA=pid,
        titre="Conv test messages",
        temperature=0.7,
        top_p=1.0,
        max_tokens=150,
        is_collab=False,
        token_collab=None,
    )
    return cdao.create(c)


def test_add_insere_message_et_renseigne_id_et_created_at():
    mdao = MessageDao()
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = _create_user()
    perso = _create_personnage(user.id_utilisateur)
    conv = _create_conversation(user.id_utilisateur, perso.id_personnageIA)

    msg = Message(
        id_message=None,
        id_conversation=conv.id_conversation,
        expediteur="utilisateur",
        id_utilisateur=user.id_utilisateur,
        contenu="Bonjour DAO message",
    )

    created = mdao.add(msg)

    assert created.id_message is not None
    assert created.created_at is not None

    # Vérifie qu'il est bien en base via list_for_conversation
    messages = mdao.list_for_conversation(conv.id_conversation)
    ids = [m.id_message for m in messages]
    assert created.id_message in ids

    # Nettoyage : on supprime d'abord la conversation (ce qui supprime les messages),
    # puis l'utilisateur.
    cdao.delete(conv.id_conversation)
    udao.delete(user.id_utilisateur)


def test_list_for_conversation_retourne_les_messages_dans_l_ordre():
    mdao = MessageDao()
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = _create_user()
    perso = _create_personnage(user.id_utilisateur)
    conv = _create_conversation(user.id_utilisateur, perso.id_personnageIA)

    m1 = mdao.add(
        Message(
            id_message=None,
            id_conversation=conv.id_conversation,
            expediteur="utilisateur",
            id_utilisateur=user.id_utilisateur,
            contenu="Premier message",
        )
    )
    m2 = mdao.add(
        Message(
            id_message=None,
            id_conversation=conv.id_conversation,
            expediteur="IA",
            id_utilisateur=None,
            contenu="Deuxième message",
        )
    )

    liste = mdao.list_for_conversation(conv.id_conversation)
    ids = [m.id_message for m in liste]

    # On attend l'ordre d'insertion : m1 puis m2
    assert ids[0] == m1.id_message
    assert ids[1] == m2.id_message

    cdao.delete(conv.id_conversation)
    udao.delete(user.id_utilisateur)


def test_recherche_mots_message_filtre_par_utilisateur_et_contenu():
    mdao = MessageDao()
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user1 = _create_user()
    user2 = _create_user()

    perso1 = _create_personnage(user1.id_utilisateur)
    perso2 = _create_personnage(user2.id_utilisateur)

    conv1 = _create_conversation(user1.id_utilisateur, perso1.id_personnageIA)
    conv2 = _create_conversation(user2.id_utilisateur, perso2.id_personnageIA)

    # Messages pour user1
    mdao.add(
        Message(
            id_message=None,
            id_conversation=conv1.id_conversation,
            expediteur="utilisateur",
            id_utilisateur=user1.id_utilisateur,
            contenu="J'adore la pizza au fromage",
        )
    )
    mdao.add(
        Message(
            id_message=None,
            id_conversation=conv1.id_conversation,
            expediteur="utilisateur",
            id_utilisateur=user1.id_utilisateur,
            contenu="Rien à voir avec le mot clé",
        )
    )

    # Message pour user2 avec le même mot, doit être ignoré
    mdao.add(
        Message(
            id_message=None,
            id_conversation=conv2.id_conversation,
            expediteur="utilisateur",
            id_utilisateur=user2.id_utilisateur,
            contenu="Moi aussi j'aime la pizza",
        )
    )

    res = mdao.recherche_mots_message(user1.id_utilisateur, "pizza", limite=10)

    # Tous les résultats doivent appartenir à user1 et contenir "pizza"
    assert len(res) >= 1
    for row in res:
        assert row["id_utilisateur"] == user1.id_utilisateur
        assert "pizza" in row["contenu"].lower()

    # Nettoyage : d'abord les conversations (ce qui supprime les messages),
    # puis les utilisateurs.
    cdao.delete(conv1.id_conversation)
    cdao.delete(conv2.id_conversation)
    udao.delete(user1.id_utilisateur)
    udao.delete(user2.id_utilisateur)
