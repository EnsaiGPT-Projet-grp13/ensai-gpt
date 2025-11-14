import pytest

from dao.conversation_dao import ConversationDao



#pytest.setup_test_environment()

def test_recherche_mots_titre_okcomplet(conversation_existante, setup_test_environment):
    """Recherche par id d'un utilisateur existant"""
    # GIVEN
    id_utilisateur = conversation_existante.id_proprio
    mots = "test"  
    limite = 50 

    # WHEN
    conversation = ConversationDao().recherche_mots_titre(id_utilisateur, mots, limite)

    # THEN
    assert conversation is not None
    assert conversation.id_conversation == conversation_existante.id_conversation
    assert conversation.titre == conversation_existante.titre
    assert conversation.update_at == conversation_existante.update_at
