# tests/test_dao/test_conversation_dao.py

import uuid
from datetime import date

from dao.utilisateur_dao import UtilisateurDao
from dao.personnage_ia_dao import PersonnageIADao
from dao.conversation_dao import ConversationDao
from dao.db import DBConnection

from objects.utilisateur import Utilisateur
from objects.personnage_ia import PersonnageIA
from objects.conversation import Conversation


# --- Petits helpers pour créer des données de test ---


def _create_user() -> Utilisateur:
    """Crée un utilisateur en base et le retourne."""
    udao = UtilisateurDao()
    mail = f"conv_user_{uuid.uuid4().hex[:8]}@example.com"
    u = Utilisateur(
        id_utilisateur=None,
        prenom="Conv",
        nom="User",
        mail=mail,
        mdp_hash="HASH_TEST",
        naiss=date(2000, 1, 1),
    )
    return udao.create(u)


def _create_personnage(owner_id: int) -> PersonnageIA:
    """Crée un personnage IA rattaché à un utilisateur."""
    pdao = PersonnageIADao()
    p = PersonnageIA(
        id_personnageIA=None,
        name="BotConv_" + uuid.uuid4().hex[:4],
        system_prompt="Bot pour tests de conversation.",
        created_by=owner_id,
    )
    return pdao.create(p)


def _create_conversation(owner_id: int, pid: int, *, titre: str = "Conv de test",
                         is_collab: bool = False, token_collab=None) -> Conversation:
    """Crée une conversation simple."""
    cdao = ConversationDao()
    c = Conversation(
        id_conversation=None,
        id_proprio=owner_id,
        id_personnageIA=pid,
        titre=titre,
        temperature=0.7,
        top_p=1.0,
        max_tokens=150,
        is_collab=is_collab,
        token_collab=token_collab,
    )
    return cdao.create(c)


# --- Tests ---


def test_create_et_find_by_id_retournent_la_meme_conversation():
    """create doit insérer une conversation et find_by_id doit la retrouver."""
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = _create_user()
    perso = _create_personnage(user.id_utilisateur)
    conv = _create_conversation(user.id_utilisateur, perso.id_personnageIA, titre="Ma première conv")

    # Récupération par id
    relu = cdao.find_by_id(conv.id_conversation)

    assert relu is not None
    assert relu.id_conversation == conv.id_conversation
    assert relu.id_proprio == user.id_utilisateur
    assert relu.id_personnageIA == perso.id_personnageIA
    assert relu.titre == "Ma première conv"

    # Nettoyage : l'utilisateur suffit, les FK feront le reste
    udao.delete(user.id_utilisateur)


def test_find_by_token_retourne_la_conversation_collaborative():
    """find_by_token doit renvoyer la conversation si le token correspond."""
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = _create_user()
    perso = _create_personnage(user.id_utilisateur)

    token = "TOK" + uuid.uuid4().hex[:5].upper()
    conv = _create_conversation(
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


def test_add_participant_ajoute_une_ligne_dans_conv_utilisateur():
    """add_participant doit insérer une ligne dans la table d'association conv_utilisateur."""
    udao = UtilisateurDao()
    cdao = ConversationDao()
    conn = DBConnection().connection

    # Propriétaire + perso + conv
    owner = _create_user()
    perso = _create_personnage(owner.id_utilisateur)
    conv = _create_conversation(owner.id_utilisateur, perso.id_personnageIA)

    # Un autre utilisateur qui sera ajouté comme participant
    guest = _create_user()

    cdao.add_participant(guest.id_utilisateur, conv.id_conversation)

    # Vérification directe dans la table conv_utilisateur
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM projetgpt.conv_utilisateur
            WHERE id_utilisateur = %s AND id_conversation = %s
            """,
            (guest.id_utilisateur, conv.id_conversation),
        )
        row = cur.fetchone()

    assert row is not None

    # Nettoyage : supprimer les 2 users
    udao.delete(guest.id_utilisateur)
    udao.delete(owner.id_utilisateur)


def test_liste_proprietaire_pour_utilisateur_retourne_ses_conversations():
    """liste_proprietaire_pour_utilisateur doit retourner les conversations dont l'utilisateur est proprio."""
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user = _create_user()
    perso = _create_personnage(user.id_utilisateur)

    conv1 = _create_conversation(user.id_utilisateur, perso.id_personnageIA, titre="conv A")
    conv2 = _create_conversation(user.id_utilisateur, perso.id_personnageIA, titre="conv B")

    liste = cdao.liste_proprietaire_pour_utilisateur(user.id_utilisateur, limite=10)

    ids = {c.id_conversation for c in liste}
    assert conv1.id_conversation in ids
    assert conv2.id_conversation in ids
    for c in liste:
        assert c.id_proprio == user.id_utilisateur

    udao.delete(user.id_utilisateur)


def test_recherche_mots_titre_filtre_par_mot_et_utilisateur():
    """recherche_mots_titre doit filtrer sur le titre et sur l'utilisateur."""
    udao = UtilisateurDao()
    cdao = ConversationDao()

    user1 = _create_user()
    user2 = _create_user()

    perso1 = _create_personnage(user1.id_utilisateur)
    perso2 = _create_personnage(user2.id_utilisateur)

    # Conversations de user1
    c_match = _create_conversation(user1.id_utilisateur, perso1.id_personnageIA, titre="Projet pizza ENSAI")
    _create_conversation(user1.id_utilisateur, perso1.id_personnageIA, titre="Autre sujet sans mot clé")

    # Conversation de user2 avec le même mot, doit être ignorée pour user1
    _create_conversation(user2.id_utilisateur, perso2.id_personnageIA, titre="Pizza secrète")

    res = cdao.recherche_mots_titre(user1.id_utilisateur, "pizza", limite=10)

    assert len(res) >= 1
    # On vérifie qu'au moins une des conversations de user1 apparaît
    ids = {row["id_conversation"] for row in res}
    assert c_match.id_conversation in ids

    # Les titres doivent contenir 'pizza'
    for row in res:
        assert "pizza" in row["titre"].lower()

    udao.delete(user1.id_utilisateur)
    udao.delete(user2.id_utilisateur)
