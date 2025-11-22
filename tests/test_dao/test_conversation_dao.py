import uuid

from dao.conversation_dao import ConversationDao
from dao.utilisateur_dao import UtilisateurDao
from tests.test_dao.helpers_dao import (
    create_test_conversation,
    create_test_personnage,
    create_test_user,
)


def test_create_et_find_by_id_retournent_la_meme_conversation():
    """create doit insérer une conversation et find_by_id doit la retrouver."""
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = create_test_user(email_prefix="conv_user")
    perso = create_test_personnage(user.id_utilisateur, prefix="BotConv")
    conv = create_test_conversation(
        user.id_utilisateur,
        perso.id_personnageIA,
        titre="Ma première conv",
    )

    relu = cdao.find_by_id(conv.id_conversation)

    assert relu is not None
    assert relu.id_conversation == conv.id_conversation
    assert relu.id_proprio == user.id_utilisateur
    assert relu.id_personnageIA == perso.id_personnageIA
    assert relu.titre == "Ma première conv"

    udao.delete(user.id_utilisateur)


def test_find_by_token_retourne_la_conversation_collaborative():
    """find_by_token doit renvoyer la conversation si le token correspond."""
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = create_test_user(email_prefix="conv_token_user")
    perso = create_test_personnage(user.id_utilisateur, prefix="BotConv")

    token = "TOK" + uuid.uuid4().hex[:5].upper()
    conv = create_test_conversation(
        user.id_utilisateur,
        perso.id_personnageIA,
        titre="Conv collab",
        is_collab=True,
        token_collab=token,
    )

    relu = cdao.find_by_token(token)

    assert relu is not None
    assert relu.id_conversation == conv.id_conversation
    assert relu.is_collab is True
    assert relu.token_collab == token

    udao.delete(user.id_utilisateur)



def test_recherche_mots_titre_filtre_par_mot_et_utilisateur():
    """recherche_mots_titre doit filtrer sur le titre et sur l'utilisateur."""
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user1 = create_test_user(email_prefix="conv_user1")
    user2 = create_test_user(email_prefix="conv_user2")

    perso1 = create_test_personnage(user1.id_utilisateur, prefix="BotConv1")
    perso2 = create_test_personnage(user2.id_utilisateur, prefix="BotConv2")

    c_match = create_test_conversation(
        user1.id_utilisateur,
        perso1.id_personnageIA,
        titre="Projet pizza ENSAI",
    )
    create_test_conversation(
        user1.id_utilisateur,
        perso1.id_personnageIA,
        titre="Autre sujet sans mot clé",
    )

    create_test_conversation(
        user2.id_utilisateur,
        perso2.id_personnageIA,
        titre="Pizza secrète",
    )

    res = cdao.recherche_mots_titre(user1.id_utilisateur, "pizza", limite=10)

    assert len(res) >= 1
    ids = {row["id_conversation"] for row in res}
    assert c_match.id_conversation in ids

    for row in res:
        assert "pizza" in row["titre"].lower()

    udao.delete(user1.id_utilisateur)
    udao.delete(user2.id_utilisateur)
