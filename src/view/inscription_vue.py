from datetime import date
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from service.auth_service import is_valid_email, is_valid_password, AuthService
from view.accueil_vue import AccueilVue

class InscriptionVue(VueAbstraite):
    """Vue d'inscription (DB)"""

    def choisir_menu(self):

        # --- Prénom ---
        while True:
            prenom = (inquirer.text(message="Prénom :").execute() or "").strip()
            if prenom:
                break
            print("Le prénom ne peut pas être vide.\n")

        # --- Nom ---
        while True:
            nom = (inquirer.text(message="Nom :").execute() or "").strip()
            if nom:
                break
            print("Le nom ne peut pas être vide.\n")

        # --- Email ---
        while True:
            mail = (inquirer.text(message="Email :").execute() or "").strip().lower()
            try:
                is_valid_email(mail)
                break
            except ValueError as e:
                print(f"{e}\nRéessaie.\n")

        # --- Mot de passe (avec boucle de retry et confirmation) ---
        while True:
            mdp = inquirer.secret(message="Mot de passe :").execute() or ""
            try:
                is_valid_password(mdp)
            except ValueError as e:
                print(f"{e}\nEssaye à nouveau.\n")
                continue
            
            MAX_TRIES = 3
            for i in range(1, MAX_TRIES + 1):
                mdp2 = inquirer.secret(message="Confirme le mot de passe :").execute() or ""
                if mdp != mdp2 and i < MAX_TRIES:
                    print(f"Les mots de passe ne correspondent pas. Réessaie. (essai {i}/{MAX_TRIES}) \n")
                    continue
                else:
                    return AccueilVue("Confirmation de mot de passe incorrecte (3 tentatives).")


        # --- Date de naissance ---
        while True:
            naiss_str = (inquirer.text(message="Date de naissance (YYYY-MM-DD) :").execute() or "").strip()
            try:
                naiss = date.fromisoformat(naiss_str)
                break
            except Exception:
                print("Date invalide. Format attendu : YYYY-MM-DD\n")

        # --- Inscription ---
        try:
            user = AuthService().inscrire(prenom, nom, mail, mdp, naiss)
        except ValueError as e:
            return AccueilVue(f"Inscription impossible : {e}")

        return AccueilVue(f"Compte créé pour {user.prenom} {user.nom}. Vous pouvez vous connecter.")
