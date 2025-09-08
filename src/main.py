# src/main.py
import logging
import os
from dotenv import load_dotenv, find_dotenv

from utils.log_init import initialiser_logs
from view.accueil.accueil_vue import AccueilVue


def charger_env():
    """Charge .env où qu'il soit (racine du projet en général)."""
    # Cherche .env à partir du cwd; si introuvable, tente ../.env
    dotenv_path = find_dotenv(filename=".env", usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, override=True)
    else:
        load_dotenv("../.env", override=True)


def main():
    # 1) .env + logs
    charger_env()
    initialiser_logs("Application")

    # 2) Vue de départ
    vue_courante = AccueilVue("Bienvenue — Utilisateurs & Chat IA")

    # 3) Boucle d’orchestration
    nb_erreurs = 0
    ERREUR_MAX = 100

    while vue_courante is not None:
        if nb_erreurs > ERREUR_MAX:
            print("Le programme recense trop d'erreurs et va s'arrêter.")
            logging.error("Abandon après trop d'erreurs.")
            break

        try:
            # Certaines vues ont afficher(), d'autres pas → on s'adapte
            if hasattr(vue_courante, "afficher") and callable(vue_courante.afficher):
                vue_courante.afficher()

            # Chaque vue doit **retourner la vue suivante** (ou None pour quitter)
            vue_courante = vue_courante.choisir_menu()

        except KeyboardInterrupt:
            print("\nInterruption par l’utilisateur. Au revoir.")
            logging.info("Interruption clavier (CTRL+C)")
            break

        except Exception as e:
            logging.error(f"{type(e).__name__} : {e}", exc_info=True)
            nb_erreurs += 1
            # On rebascule proprement sur l’accueil avec un message lisible
            vue_courante = AccueilVue(
                "Une erreur est survenue, retour au menu principal.\n"
                "Consultez les logs pour plus d'informations."
            )

    print("----------------------------------")
    print("Au revoir")
    logging.info("Fin de l'application")


if __name__ == "__main__":
    main()
