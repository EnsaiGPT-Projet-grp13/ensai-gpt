from dao.utilisateur_dao import UtilisateurDao
from dao.conversation_dao import ConversationDao
from dao.message_dao import MessageDao

from objects.message import Message

from tests.test_dao.helpers_dao import (
    create_test_user,
    create_test_personnage,
    create_test_conversation,
)


def test_add_insere_message_et_renseigne_id_et_created_at():
    mdao = MessageDao()
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = create_test_user(email_prefix="msg_user")
    perso = create_test_personnage(user.id_utilisateur, prefix="BotMsg")
    conv = create_test_conversation(
        user.id_utilisateur,
        perso.id_personnageIA,
        titre="Conv test messages",
    )

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

    messages = mdao.list_for_conversation(conv.id_conversation)
    ids = [m.id_message for m in messages]
    assert created.id_message in ids

    cdao.delete(conv.id_conversation)
    udao.delete(user.id_utilisateur)


def test_list_for_conversation_retourne_les_messages_dans_l_ordre():
    mdao = MessageDao()
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = create_test_user(email_prefix="msg_user_list")
    perso = create_test_personnage(user.id_utilisateur, prefix="BotMsg")
    conv = create_test_conversation(
        user.id_utilisateur,
        perso.id_personnageIA,
        titre="Conv test messages",
    )

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

    assert ids[0] == m1.id_message
    assert ids[1] == m2.id_message

    cdao.delete(conv.id_conversation)
    udao.delete(user.id_utilisateur)
