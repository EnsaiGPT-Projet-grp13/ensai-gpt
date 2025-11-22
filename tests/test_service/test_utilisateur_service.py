import pytest
from unittest.mock import Mock

from service.utilisateur_service import UtilisateurService, DEFAULT_PERSONAS
from utils.securite import hash_password
from objects.utilisateur import Utilisateur


@pytest.fixture
def service_utilisateur():
    """
    Fournit un UtilisateurService avec DAO mockés pour tous les tests.
    """
    service = UtilisateurService()
    service.dao = Mock()
    service.persona_dao = Mock()
    return service


def test_creer_valide_appelle_validations_et_dao(service_utilisateur, monkeypatch):
    # On neutralise les validations pour ce test
    monkeypatch.setattr("service.utilisateur_service.is_valid_email", lambda m: True)
    monkeypatch.setattr("service.utilisateur_service.is_valid_password", lambda p: True)

    service_utilisateur.dao.exists_mail.return_value = False

    # On stub add_default_persoIA pour vérifier l'appel
    service_utilisateur.add_default_persoIA = Mock(return_value=len(DEFAULT_PERSONAS))

    def fake_create(u):
        # Le DAO renvoie l'utilisateur avec un id
        u.id_utilisateur = 42
        return u

    service_utilisateur.dao.create.side_effect = fake_create

    u = service_utilisateur.creer(
        prenom="Alice",
        nom="Test",
        mail="  Alice@Test.com ",
        mdp="secret",
        naiss="2000-01-01",
    )

    mail_norm = "alice@test.com"
    # Vérif objet retourné
    assert isinstance(u, Utilisateur)
    assert u.id_utilisateur == 42
    assert u.prenom == "Alice"
    assert u.mail == mail_norm

    # Vérif exists_mail sur mail normalisé
    service_utilisateur.dao.exists_mail.assert_called_once_with(mail_norm)

    # Vérif hash
    expected_hash = hash_password("secret", mail_norm)
    args, _ = service_utilisateur.dao.create.call_args
    u_passe = args[0]
    assert isinstance(u_passe, Utilisateur)
    assert u_passe.mdp_hash == expected_hash

    # Vérif ajout default personas
    service_utilisateur.add_default_persoIA.assert_called_once_with(42)


def test_creer_echoue_si_mail_deja_utilise(service_utilisateur, monkeypatch):
    monkeypatch.setattr("service.utilisateur_service.is_valid_email", lambda m: True)
    monkeypatch.setattr("service.utilisateur_service.is_valid_password", lambda p: True)

    service_utilisateur.dao.exists_mail.return_value = True

    with pytest.raises(ValueError) as exc:
        service_utilisateur.creer("Bob", "Test", "bob@test.com", "mdp", "1999-01-01")

    assert "existe déjà" in str(exc.value)
    service_utilisateur.dao.create.assert_not_called()


def test_creer_echoue_si_email_invalide(service_utilisateur, monkeypatch):
    def fake_is_valid_email(mail):
        raise ValueError("email invalide")

    monkeypatch.setattr(
        "service.utilisateur_service.is_valid_email", fake_is_valid_email
    )
    monkeypatch.setattr("service.utilisateur_service.is_valid_password", lambda p: True)

    service_utilisateur.dao.exists_mail.return_value = False

    with pytest.raises(ValueError):
        service_utilisateur.creer(
            "Alice", "Test", "mauvais_mail", "secret", "2000-01-01"
        )

    service_utilisateur.dao.create.assert_not_called()


def test_creer_echoue_si_mdp_invalide(service_utilisateur, monkeypatch):
    monkeypatch.setattr("service.utilisateur_service.is_valid_email", lambda m: True)

    def fake_is_valid_password(p):
        raise ValueError("mdp invalide")

    monkeypatch.setattr(
        "service.utilisateur_service.is_valid_password", fake_is_valid_password
    )

    service_utilisateur.dao.exists_mail.return_value = False

    with pytest.raises(ValueError):
        service_utilisateur.creer("Alice", "Test", "alice@test.com", "xx", "2000-01-01")

    service_utilisateur.dao.create.assert_not_called()


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


def test_se_connecter_retourne_none_si_mail_inconnu(service_utilisateur):
    service_utilisateur.dao.find_by_mail.return_value = None

    user = service_utilisateur.se_connecter("unknown@test.com", "mdp")

    assert user is None
    service_utilisateur.dao.find_by_mail.assert_called_once_with("unknown@test.com")


def test_se_connecter_retourne_user_si_mdp_valide_salt_email(service_utilisateur):
    mdp_clair = "secret"
    mail = "a@test.com"
    hashed = hash_password(mdp_clair, mail)
    u = Utilisateur(1, "A", "A", mail, hashed, "2000-01-01")
    service_utilisateur.dao.find_by_mail.return_value = u

    user = service_utilisateur.se_connecter(
        "A@test.com", mdp_clair
    )  # test normalisation

    assert user is u
    service_utilisateur.dao.find_by_mail.assert_called_once_with("a@test.com")



def test_se_connecter_retourne_none_si_mdp_invalide(service_utilisateur):
    hashed = hash_password("autre_mdp", "a@test.com")
    u = Utilisateur(1, "A", "A", "a@test.com", hashed, "2000-01-01")
    service_utilisateur.dao.find_by_mail.return_value = u

    user = service_utilisateur.se_connecter("a@test.com", "secret")

    assert user is None
    service_utilisateur.dao.find_by_mail.assert_called_once_with("a@test.com")


def test_mail_deja_utilise_delegue_exists_mail(service_utilisateur):
    service_utilisateur.dao.exists_mail.return_value = True

    res = service_utilisateur.mail_deja_utilise("a@test.com")

    assert res is True
    service_utilisateur.dao.exists_mail.assert_called_once_with("a@test.com")


def test_changer_email_retourne_false_si_user_introuvable(service_utilisateur):
    service_utilisateur.dao.find_by_id.return_value = None

    ok, msg = service_utilisateur.changer_email(1, "new@test.com", "mdp")

    assert ok is False
    assert "introuvable" in msg
    service_utilisateur.dao.update_mail_utilisateur.assert_not_called()
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_email_retourne_false_si_mdp_incorrect(service_utilisateur):
    # utilisateur avec mail old@test.com et hash qui ne correspond pas à "mdp"
    u = Utilisateur(
        1,
        "A",
        "A",
        "old@test.com",
        hash_password("autre", "old@test.com"),
        "2000-01-01",
    )
    service_utilisateur.dao.find_by_id.return_value = u

    ok, msg = service_utilisateur.changer_email(1, "new@test.com", "mdp")

    assert ok is False
    assert "Mot de passe incorrect" in msg
    service_utilisateur.dao.update_mail_utilisateur.assert_not_called()
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_email_retourne_false_si_nouvel_email_invalide(
    service_utilisateur, monkeypatch
):
    old_mail = "old@test.com"
    u = Utilisateur(1, "A", "A", old_mail, hash_password("mdp", old_mail), "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    def fake_is_valid_email(mail):
        raise ValueError("format invalide")

    monkeypatch.setattr(
        "service.utilisateur_service.is_valid_email", fake_is_valid_email
    )

    ok, msg = service_utilisateur.changer_email(1, "new@", "mdp")

    assert ok is False
    assert "Email invalide" in msg
    service_utilisateur.dao.exists_mail.assert_not_called()
    service_utilisateur.dao.update_mail_utilisateur.assert_not_called()
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_email_retourne_false_si_nouvel_email_deja_pris(
    service_utilisateur, monkeypatch
):
    old_mail = "old@test.com"
    u = Utilisateur(1, "A", "A", old_mail, hash_password("mdp", old_mail), "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    monkeypatch.setattr("service.utilisateur_service.is_valid_email", lambda m: True)
    service_utilisateur.dao.exists_mail.return_value = True

    ok, msg = service_utilisateur.changer_email(1, "new@test.com", "mdp")

    assert ok is False
    assert "existe déjà" in msg
    service_utilisateur.dao.update_mail_utilisateur.assert_not_called()
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_email_retourne_false_si_update_echoue(
    service_utilisateur, monkeypatch
):
    old_mail = "old@test.com"
    new_mail = "new@test.com"
    u = Utilisateur(1, "A", "A", old_mail, hash_password("mdp", old_mail), "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    monkeypatch.setattr("service.utilisateur_service.is_valid_email", lambda m: True)
    service_utilisateur.dao.exists_mail.return_value = False

    # on simule un échec de mise à jour en base
    service_utilisateur.dao.update_mail_utilisateur.return_value = False
    service_utilisateur.dao.update_mot_de_passe.return_value = True

    ok, msg = service_utilisateur.changer_email(1, new_mail, "mdp")

    assert ok is False
    assert "Échec" in msg
    assert u.mail == new_mail  # l'objet en mémoire a été modifié
    service_utilisateur.dao.update_mail_utilisateur.assert_called_once_with(u)
    service_utilisateur.dao.update_mot_de_passe.assert_called_once()


def test_changer_email_succes(service_utilisateur, monkeypatch):
    old_mail = "old@test.com"
    new_mail = "new@test.com"
    mdp = "mdp"

    u = Utilisateur(1, "A", "A", old_mail, hash_password(mdp, old_mail), "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    monkeypatch.setattr("service.utilisateur_service.is_valid_email", lambda m: True)
    service_utilisateur.dao.exists_mail.return_value = False
    service_utilisateur.dao.update_mail_utilisateur.return_value = True
    service_utilisateur.dao.update_mot_de_passe.return_value = True

    ok, msg = service_utilisateur.changer_email(1, new_mail, mdp)

    assert ok is True
    assert "succès" in msg

    assert u.mail == new_mail
    expected_hash = hash_password(mdp, new_mail)
    service_utilisateur.dao.update_mail_utilisateur.assert_called_once_with(u)
    service_utilisateur.dao.update_mot_de_passe.assert_called_once_with(
        1, expected_hash
    )


def test_changer_identite_retourne_false_si_user_introuvable(service_utilisateur):
    service_utilisateur.dao.find_by_id.return_value = None

    ok, msg = service_utilisateur.changer_identite(1, "Nouveau", "Nom")

    assert ok is False
    assert "introuvable" in msg
    service_utilisateur.dao.update_identite.assert_not_called()


def test_changer_identite_retourne_false_si_prenom_vide(service_utilisateur):
    u = Utilisateur(1, "AncienPrenom", "AncienNom", "a@test.com", "HASH", "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    ok, msg = service_utilisateur.changer_identite(1, "   ", "Nom")

    assert ok is False
    assert "prénom" in msg
    service_utilisateur.dao.update_identite.assert_not_called()


def test_changer_identite_retourne_false_si_nom_vide(service_utilisateur):
    u = Utilisateur(1, "AncienPrenom", "AncienNom", "a@test.com", "HASH", "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u

    ok, msg = service_utilisateur.changer_identite(1, "Prenom", "   ")

    assert ok is False
    assert "nom" in msg
    service_utilisateur.dao.update_identite.assert_not_called()


def test_changer_identite_succes_met_a_jour_prenom_nom(service_utilisateur):
    u = Utilisateur(1, "AncienPrenom", "AncienNom", "a@test.com", "HASH", "2000-01-01")
    service_utilisateur.dao.find_by_id.return_value = u
    service_utilisateur.dao.update_identite.return_value = True

    ok, msg = service_utilisateur.changer_identite(1, "NouveauPrenom", "NouveauNom")

    assert ok is True
    assert "succès" in msg
    assert u.prenom == "NouveauPrenom"
    assert u.nom == "NouveauNom"
    service_utilisateur.dao.update_identite.assert_called_once_with(u)


def test_changer_mot_de_passe_retourne_false_si_user_introuvable(service_utilisateur):
    service_utilisateur.dao.find_by_id.return_value = None

    ok, msg = service_utilisateur.changer_mot_de_passe(1, "old", "new")

    assert ok is False
    assert "introuvable" in msg
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_mot_de_passe_retourne_false_si_ancien_mdp_incorrect(service_utilisateur):
    mail = "a@test.com"
    u = Utilisateur(
        1,
        "A",
        "A",
        mail,
        hash_password("autre_mdp", mail),  # ne correspond pas à "ancien"
        "2000-01-01",
    )
    service_utilisateur.dao.find_by_id.return_value = u

    ok, msg = service_utilisateur.changer_mot_de_passe(1, "ancien", "nouveau")

    assert ok is False
    assert "incorrect" in msg
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_mot_de_passe_retourne_false_si_meme_mdp(service_utilisateur):
    mail = "a@test.com"
    ancien = "secret"
    u = Utilisateur(
        1,
        "A",
        "A",
        mail,
        hash_password(ancien, mail),
        "2000-01-01",
    )
    service_utilisateur.dao.find_by_id.return_value = u

    ok, msg = service_utilisateur.changer_mot_de_passe(1, ancien, ancien)

    assert ok is False
    assert "différent" in msg
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_mot_de_passe_retourne_false_si_nouveau_mdp_invalide(
    service_utilisateur, monkeypatch
):
    mail = "a@test.com"
    ancien = "secret"
    u = Utilisateur(
        1,
        "A",
        "A",
        mail,
        hash_password(ancien, mail),
        "2000-01-01",
    )
    service_utilisateur.dao.find_by_id.return_value = u

    def fake_is_valid_password(p):
        raise ValueError("mdp trop court")

    monkeypatch.setattr(
        "service.utilisateur_service.is_valid_password", fake_is_valid_password
    )

    ok, msg = service_utilisateur.changer_mot_de_passe(1, ancien, "xx")

    assert ok is False
    assert "Mot de passe invalide" in msg
    service_utilisateur.dao.update_mot_de_passe.assert_not_called()


def test_changer_mot_de_passe_succes_update_hash(service_utilisateur, monkeypatch):
    mail = "a@test.com"
    ancien = "ancien_mdp"
    nouveau = "nouveau_mdp_plus_long"

    u = Utilisateur(
        1,
        "A",
        "A",
        mail,
        hash_password(ancien, mail),
        "2000-01-01",
    )
    service_utilisateur.dao.find_by_id.return_value = u

    # validation OK
    monkeypatch.setattr(
        "service.utilisateur_service.is_valid_password", lambda p: True
    )
    service_utilisateur.dao.update_mot_de_passe.return_value = True

    ok, msg = service_utilisateur.changer_mot_de_passe(1, ancien, nouveau)

    assert ok is True
    assert "succès" in msg

    expected_hash = hash_password(nouveau, mail)
    service_utilisateur.dao.update_mot_de_passe.assert_called_once_with(1, expected_hash)
