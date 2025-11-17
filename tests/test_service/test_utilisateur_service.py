# tests/test_service/test_utilisateur_service.py

import pytest
from unittest.mock import Mock

from service.utilisateur_service import UtilisateurService, DEFAULT_PERSONAS
from utils.securite import hash_password
from objects.utilisateur import Utilisateur
from objects.personnage_ia import PersonnageIA


@pytest.fixture
def service_utilisateur():
    """
    Fournit un UtilisateurService avec DAO mockés pour tous les tests.
    """
    service = UtilisateurService()
    service.dao = Mock()
    service.persona_dao = Mock()
    return service


# =========================
# Tests de creer()
# =========================

def test_creer_appelle_dao_create_et_retourne_utilisateur_si_succes(service_utilisateur):
    service_utilisateur.dao.create.return_value = True

    u = service_utilisateur.creer(
        prenom="Alice",
        nom="Test",
        mail="alice@test.com",
        mdp="secret",
        naiss="2000-01-01",
    )

    # On vérifie la forme de l'objet retourné
    assert isinstance(u, Utilisateur)
    assert u.prenom == "Alice"
    assert u.mail == "alice@test.com"

    # Le hash doit correspondre à la vraie fonction hash_password
    expected_hash = hash_password("secret")
    assert u.mdp_hash == expected_hash

    # Le DAO doit être appelé une fois avec un Utilisateur
    service_utilisateur.dao.create.assert_called_once()
    args, kwargs = service_utilisateur.dao.create.call_args
    u_passe = args[0]
    assert isinstance(u_passe, Utilisateur)
    assert u_passe.prenom == "Alice"
    assert u_passe.mail == "alice@test.com"


def test_creer_retourne_none_si_create_echoue(service_utilisateur):
    service_utilisateur.dao.create.return_value = False

    u = service_utilisateur.creer("Bob", "Test", "bob@test.com", "mdp", "1999-01-01")

    assert u is None
    service_utilisateur.dao.create.assert_called_once()


# =========================
# Tests de lister_tous()
# =========================

def test_lister_tous_masque_mdp_par_defaut(service_utilisateur):
    user1 = Utilisateur(1, "A", "A", "a@test.com", "HASH1", "2000-01-01")
    user2 = Utilisateur(2, "B", "B", "b@test.com", "HASH2", "2001-01-01")
    service_utilisateur.dao.lister_tous.return_value = [user1, user2]

    users = service_utilisateur.lister_tous()

    assert len(users) == 2
    assert users[0].mdp_hash is None
    assert users[1].mdp_hash is None
    service_utilisateur.dao.lister_tous.assert_called_once()


def test_lister_tous_conserve_mdp_si_inclure_mdp_true(service_utilisateur):
    user1 = Utilisateur(1, "A", "A", "a@test.com", "HASH1", "2000-01-01")
    service_utilisateur.dao.lister_tous.return_value = [user1]

    users = service_utilisateur.lister_tous(inclure_mdp=True)

    assert users[0].mdp_hash == "HASH1"
    service_utilisateur.dao.lister_tous.assert_called_once()


# =========================
# Tests de trouver_par_id() / supprimer()
# =========================

def test_trouver_par_id_delegue_au_dao(service_utilisateur):
    u = Utilisateur(1, "A", "A", "a@test.com", "HASH", "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    res = service_utilisateur.trouver_par_id(1)

    assert res is u
    service_utilisateur.dao.find_by_id.assert_called_once_with(1)


def test_supprimer_delegue_delete(service_utilisateur):
    u = Utilisateur(
        id_utilisateur=1,
        prenom="A",
        nom="A",
        mail="a@test.com",
        mdp_hash="HASH",
        naiss="2000-01-01",
    )
    service_utilisateur.dao.delete.return_value = True

    ok = service_utilisateur.supprimer(u)

    assert ok is True
    service_utilisateur.dao.delete.assert_called_once_with(1)


# =========================
# Tests de modifier()
# =========================

def test_modifier_sans_rehash_appelle_update_et_retourne_utilisateur(service_utilisateur):
    u = Utilisateur(1, "A", "A", "a@test.com", "HASH", "2000-01-01")
    service_utilisateur.dao.update.return_value = True

    res = service_utilisateur.modifier(u, rehash_password=False)

    assert res is u
    service_utilisateur.dao.update.assert_called_once_with(u)


def test_modifier_avec_rehash_recalcule_le_hash(service_utilisateur):
    # Ici u.mdp_hash contient le MOT DE PASSE EN CLAIR avant appel
    u = Utilisateur(1, "A", "A", "a@test.com", "mdp_en_clair", "2000-01-01")
    service_utilisateur.dao.update.return_value = True

    res = service_utilisateur.modifier(u, rehash_password=True)

    assert res is u
    expected_hash = hash_password("mdp_en_clair")
    assert u.mdp_hash == expected_hash
    service_utilisateur.dao.update.assert_called_once_with(u)


def test_modifier_retourne_none_si_update_echoue(service_utilisateur):
    u = Utilisateur(1, "A", "A", "a@test.com", "HASH", "2000-01-01")
    service_utilisateur.dao.update.return_value = False

    res = service_utilisateur.modifier(u)

    assert res is None
    service_utilisateur.dao.update.assert_called_once_with(u)


# =========================
# Tests de se_connecter()
# =========================

def test_se_connecter_retourne_none_si_mail_inconnu(service_utilisateur):
    service_utilisateur.dao.find_by_mail.return_value = None

    user = service_utilisateur.se_connecter("unknown@test.com", "mdp")

    assert user is None
    service_utilisateur.dao.find_by_mail.assert_called_once_with("unknown@test.com")


def test_se_connecter_retourne_user_si_mdp_valide(service_utilisateur):
    # On utilise le vrai hash_password pour être cohérent avec l'implémentation
    mdp_clair = "secret"
    hashed = hash_password(mdp_clair)
    u = Utilisateur(1, "A", "A", "a@test.com", hashed, "2000-01-01")
    service_utilisateur.dao.find_by_mail.return_value = u

    user = service_utilisateur.se_connecter("a@test.com", mdp_clair)

    assert user is u
    service_utilisateur.dao.find_by_mail.assert_called_once_with("a@test.com")


def test_se_connecter_retourne_none_si_mdp_invalide(service_utilisateur):
    hashed = hash_password("autre_mdp")
    u = Utilisateur(1, "A", "A", "a@test.com", hashed, "2000-01-01")
    service_utilisateur.dao.find_by_mail.return_value = u

    user = service_utilisateur.se_connecter("a@test.com", "secret")

    assert user is None
    service_utilisateur.dao.find_by_mail.assert_called_once_with("a@test.com")


# =========================
# Tests mail_deja_utilise()
# =========================

def test_mail_deja_utilise_delegue_exists_mail(service_utilisateur):
    service_utilisateur.dao.exists_mail.return_value = True

    res = service_utilisateur.mail_deja_utilise("a@test.com")

    assert res is True
    service_utilisateur.dao.exists_mail.assert_called_once_with("a@test.com")


# =========================
# Tests changer_mot_de_passe()
# =========================

def test_changer_mot_de_passe_retourne_false_si_user_introuvable(service_utilisateur):
    service_utilisateur.dao.find_by_id.return_value = None

    ok = service_utilisateur.changer_mot_de_passe(1, "old", "new")

    assert ok is False
    service_utilisateur.dao.find_by_id.assert_called_once_with(1)
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_mot_de_passe_retourne_false_si_ancien_mdp_faux(service_utilisateur):
    u = Utilisateur(1, "A", "A", "a@test.com", "HASH_OLD", "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    # On met un hash qui ne correspond pas à hash_password("ancien", u.mail)
    u.mdp_hash = hash_password("autre_mdp", u.mail)

    ok = service_utilisateur.changer_mot_de_passe(1, "ancien", "nouveau")

    assert ok is False
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_mot_de_passe_succes_update_mot_de_passe(service_utilisateur):
    u = Utilisateur(1, "A", "A", "a@test.com", "HASH_OLD", "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    # On définit le hash attendu de l'ancien mot de passe
    u.mdp_hash = hash_password("ancien", u.mail)

    ok = service_utilisateur.changer_mot_de_passe(1, "ancien", "nouveau")

    assert ok is True
    nouveau_hash_attendu = hash_password("nouveau", u.mail)
    service_utilisateur.dao.update_mot_de_passe.assert_called_once_with(1, nouveau_hash_attendu)


# =========================
# Tests changer_nom_utilisateur()
# =========================

def test_changer_nom_utilisateur_retourne_false_si_user_introuvable(service_utilisateur):
    service_utilisateur.dao.find_by_id.return_value = None

    ok = service_utilisateur.changer_nom_utilisateur(1, "NouveauNom")

    assert ok is False
    service_utilisateur.dao.update_nom_utilisateur.assert_not_called()


def test_changer_nom_utilisateur_met_a_jour_nom_et_appelle_dao(service_utilisateur):
    class FakeUser:
        def __init__(self, uid, nom):
            self.id_utilisateur = uid
            self.nom_utilisateur = nom

    fake_user = FakeUser(1, "AncienNom")
    service_utilisateur.dao.find_by_id.return_value = fake_user
    service_utilisateur.dao.update_nom_utilisateur.return_value = True

    ok = service_utilisateur.changer_nom_utilisateur(1, "NouveauNom")

    assert ok is True
    assert fake_user.nom_utilisateur == "NouveauNom"
    service_utilisateur.dao.find_by_id.assert_called_once_with(1)
    service_utilisateur.dao.update_nom_utilisateur.assert_called_once_with(fake_user)


# =========================
# Tests add_default_persoIA()
# =========================

def test_add_default_persoIA_cree_un_personnage_par_persona(service_utilisateur):
    # On suppose que DEFAULT_PERSONAS est non vide
    nb_personas = len(DEFAULT_PERSONAS)
    assert nb_personas >= 1

    service_utilisateur.persona_dao.create.return_value = True

    inserted = service_utilisateur.add_default_persoIA(user_id=5)

    assert inserted == nb_personas
    assert service_utilisateur.persona_dao.create.call_count == nb_personas

    # On vérifie les types d'objets passés
    for call in service_utilisateur.persona_dao.create.call_args_list:
        perso = call.args[0]
        assert isinstance(perso, PersonnageIA)
        assert perso.created_by == 5


def test_add_default_persoIA_compte_uniquement_les_succes(service_utilisateur):
    nb_personas = len(DEFAULT_PERSONAS)
    assert nb_personas >= 2  # on veut simuler au moins un échec

    # On fait échouer la création du DERNIER persona
    compteur = {"i": 0}

    def fake_create(perso):
        compteur["i"] += 1
        if compteur["i"] == nb_personas:
            raise Exception("Erreur d'insertion")
        return True

    service_utilisateur.persona_dao.create.side_effect = fake_create
    service_utilisateur.persona_dao.conn.rollback = Mock()

    inserted = service_utilisateur.add_default_persoIA(user_id=5)

    assert inserted == nb_personas - 1  # seul le dernier échoue
    service_utilisateur.persona_dao.conn.rollback.assert_called_once()
