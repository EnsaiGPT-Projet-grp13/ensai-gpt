# tests/test_dao/test_stats_dao.py

import numbers

from dao.stats_dao import StatsDao


def test_nbre_msgs_utilisateur_retourne_un_entier():
    """
    Vérifie que nbre_msgs_utilisateur retourne bien un entier >= 0.
    Dans le contexte de test (aucun utilisateur réellement connecté),
    on s'attend typiquement à 0, mais on ne fige pas la valeur exacte.
    """
    dao = StatsDao()
    res = dao.nbre_msgs_utilisateur()
    assert isinstance(res, numbers.Integral)
    assert res >= 0


def test_nbre_conv_utilisateurs_retourne_un_entier():
    """
    Vérifie que nbre_conv_utilisateurs retourne un entier >= 0.
    """
    dao = StatsDao()
    res = dao.nbre_conv_utilisateurs()
    assert isinstance(res, numbers.Integral)
    assert res >= 0


def test_moyenne_msg_par_conv_retourne_un_nombre():
    """
    Vérifie que moyenne_msg_par_conv retourne un nombre (float ou int) >= 0.
    Dans ta situation actuelle, ce sera probablement 0.0.
    """
    dao = StatsDao()
    res = dao.moyenne_msg_par_conv()
    assert isinstance(res, (int, float))
    assert res >= 0


def test_most_used_personnas_for_user_retourne_une_liste():
    """
    Vérifie que most_used_personnas_for_user retourne une liste.
    En l'absence de conversations, ce sera souvent [].
    """
    dao = StatsDao()
    res = dao.most_used_personas_for_user()
    assert isinstance(res, list)
    # On ne teste pas le contenu exact (dépend des données en BDD)


def test_nbre_personnages_IA_utilises_retourne_un_entier():
    """
    Vérifie que nbre_personnages_IA_utilises retourne un entier >= 0.
    """
    dao = StatsDao()
    res = dao.nbre_personnages_IA_utilises()
    assert isinstance(res, numbers.Integral)
    assert res >= 0
