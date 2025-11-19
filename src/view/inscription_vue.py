from datetime import date
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from service.auth_service import is_valid_email, is_valid_password
from view.accueil_vue import AccueilVue

class InscriptionVue(VueAbstraite):
    """Vue d'inscription (DB)"""

    def choisir_menu(self):
        def quitter_si_vide(val: str):
            """Quitte l'inscription si l'utilisateur appuie sur Entrée sans rien écrire."""
            if not val.strip():
                raise KeyboardInterrupt

        try:
            # --- Prénom ---
            while True:
                prenom = (inquirer.text(message="Prénom (Entrée vide pour quitter) :").execute() or "").strip()
                quitter_si_vide(prenom)
                if prenom:
                    break
                print("Le prénom ne peut pas être vide.\n")

            # --- Nom ---
            while True:
                nom = (inquirer.text(message="Nom (Entrée vide pour quitter) :").execute() or "").strip()
                quitter_si_vide(nom)
                if nom:
                    break
                print("Le nom ne peut pas être vide.\n")

            # --- Email ---
            from service.utilisateur_service import UtilisateurService
            service = UtilisateurService()

            while True:
                mail = (inquirer.text(message="Email (Entrée vide pour quitter) :").execute() or "").strip().lower()
                quitter_si_vide(mail)

                try:
                    is_valid_email(mail)
                except ValueError as e:
                    print(f"{e}\nRéessaie.\n")
                    continue

                # Vérifier si l’email est déjà utilisé
                if service.mail_deja_utilise(mail):
                    print("Cet email est déjà utilisé.\n")
                    continue

                break

            # --- Mot de passe ---
            while True:
                mdp = inquirer.secret(message="Mot de passe (Entrée vide pour quitter) :").execute() or ""
                quitter_si_vide(mdp)
                try:
                    is_valid_password(mdp)
                except ValueError as e:
                    print(f"{e}\nEssaye à nouveau.\n")
                    continue

                MAX_TRIES = 3
                ok = False
                for i in range(1, MAX_TRIES + 1):
                    mdp2 = inquirer.secret(message="Confirme le mot de passe (Entrée vide pour quitter) :").execute() or ""
                    quitter_si_vide(mdp2)
                    if mdp2 == mdp:
                        ok = True
                        break
                    else:
                        if i < MAX_TRIES:
                            print(f"Les mots de passe ne correspondent pas. Réessaie. (essai {i}/{MAX_TRIES})\n")
                        else:
                            return AccueilVue("Confirmation de mot de passe incorrecte (3 tentatives).")

                if ok:
                    break

            # --- Date de naissance ---
            while True:
                naiss_str = (inquirer.text(message="Date de naissance (YYYY-MM-DD, Entrée vide pour quitter) :").execute() or "").strip()
                quitter_si_vide(naiss_str)
                try:
                    naiss = date.fromisoformat(naiss_str)
                    break
                except Exception:
                    print("Date invalide. Format attendu : YYYY-MM-DD\n")

            # --- Inscription ---
            try:
                user = service.creer(prenom, nom, mail, mdp, naiss)
            except ValueError as e:
                return AccueilVue(f"Inscription impossible : {e}")

            return AccueilVue(f"Compte créé pour {user.prenom} {user.nom}. Vous pouvez vous connecter.")

        except KeyboardInterrupt:
            return AccueilVue("Inscription annulée. Retour à l'accueil.")
