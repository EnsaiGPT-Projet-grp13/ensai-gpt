import os
import pytest
from unittest.mock import patch


from src.dao.conversation_dao import ConversationDao
from src.objects.conversation import Conversation


#pytest.setup_test_environment()

def test_recherche_mots_titre_okcomplet(conversation_existante):
    """Recherche par id d'un utilisateur existant"""
    # GIVEN
    id_utilisateur = conversation_existante.id_proprio.id_utilisateur
    mots = "test"  
    limite = 50 

    # WHEN
    conversation = ConversationDao.recherche_mots_titre(id_utilisateur, mots, limite)

    # THEN
    assert conversation is not None
    assert conversation.id_conversation == conversation_existante.id_conversation
    assert conversation.titre == conversation_existante.titre
    assert conversation.update_at == conversation_existante.update_at
