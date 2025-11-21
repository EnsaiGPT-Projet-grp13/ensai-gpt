import logging

import dotenv

from utils.log_init import initialiser_logs
from view.accueil_vue import AccueilVue

if __name__ == "__main__":
    # 1) Charger l'env
    dotenv.load_dotenv(override=True)

    # 2) Logs
    initialiser_logs("Application")

    # 3) Vue de départ
    vue_courante = AccueilVue("Bienvenue")
    nb_erreurs = 0

    # 4) Boucle d'application
    while vue_courante:
        if nb_erreurs > 100:
            print("Le programme recense trop d'erreurs et va s'arrêter")
            break
        try:
            # --- affichage + navigation ---
            vue_courante.afficher()
            vue_courante = vue_courante.choisir_menu()

        except Exception as e:
            # >>> ICI le except (autour de la boucle) <<<
            print(f"[EXC] {type(e).__name__}: {e}")         # diagnostic immédiat en console
            logging.error(f"{type(e).__name__} : {e}", exc_info=True)
            nb_erreurs += 1
            vue_courante = AccueilVue(
                "Une erreur est survenue, retour au menu principal.\n"
                "Consultez les logs pour plus d'informations."
            )

    # 5) Fin propre
    print("----------------------------------")
    print("Au revoir")
    logging.info("Fin de l'application")
