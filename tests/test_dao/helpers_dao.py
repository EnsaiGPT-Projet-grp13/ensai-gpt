import uuid
from datetime import date

from dao.utilisateur_dao import UtilisateurDao
from dao.personnage_ia_dao import PersonnageIADao
from dao.conversation_dao import ConversationDao

from objects.utilisateur import Utilisateur
from objects.personnage_ia import PersonnageIA
from objects.conversation import Conversation


def make_fake_user(email_prefix: str = "test") -> Utilisateur:
    """
    Fabrique un Utilisateur en mémoire (sans id) avec un email unique.
    """
    unique = uuid.uuid4().hex[:8]
    mail = f"{email_prefix}_{unique}@example.com"
    return Utilisateur(
        id_utilisateur=None,
        prenom="Test",
        nom="User",
        mail=mail,
        mdp_hash="HASH_INIT",
        naiss=date(2000, 1, 1),
    )


def create_test_user(email_prefix: str = "user") -> Utilisateur:
    """
    Crée un utilisateur en base et le retourne.
    """
    udao = UtilisateurDao()
    u = make_fake_user(email_prefix=email_prefix)
    return udao.create(u)


def create_test_personnage(owner_id: int, prefix: str = "Bot") -> PersonnageIA:
    """
    Crée un personnage IA rattaché à un utilisateur.
    """
    pdao = PersonnageIADao()
    name = f"{prefix}_{uuid.uuid4().hex[:4]}"
    p = PersonnageIA(
        id_personnageIA=None,
        name=name,
        system_prompt="Bot de test.",
        created_by=owner_id,
    )
    return pdao.create(p)


def create_standard_personnage(
    name_prefix: str = "Std",
    system_prompt: str = "Standard de test.",
) -> PersonnageIA:
    """
    Crée un personnage IA standard (created_by = None).
    """
    pdao = PersonnageIADao()
    name = f"{name_prefix}_{uuid.uuid4().hex[:4]}"
    p = PersonnageIA(
        id_personnageIA=None,
        name=name,
        system_prompt=system_prompt,
        created_by=None,
    )
    return pdao.create(p)


def create_test_conversation(
    owner_id: int,
    pid: int,
    *,
    titre: str = "Conversation de test",
    temperature: float = 0.7,
    top_p: float = 1.0,
    max_tokens: int = 150,
    is_collab: bool = False,
    token_collab: str | None = None,
) -> Conversation:
    """
    Crée une conversation en base et la retourne.
    """
    cdao = ConversationDao()
    c = Conversation(
        id_conversation=None,
        id_proprio=owner_id,
        id_personnageIA=pid,
        titre=titre,
        created_at=None,
        updated_at=None,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        is_collab=is_collab,
        token_collab=token_collab,
    )
    return cdao.create(c)
