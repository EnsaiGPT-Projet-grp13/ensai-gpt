import regex
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator

from service.utilisateur_service import UtilisateurService
from view.vue_abstraite import VueAbstraite


class InscriptionVue(VueAbstraite):
    def choisir_menu(self):
        # Demande à l'utilisateur de saisir prénom, nom, etc.
        prenom = inquirer.text(message="Entrez votre prénom : ").execute()
        nom = inquirer.text(message="Entrez votre nom : ").execute()

        mail = inquirer.text(
            message="Entrez votre mail : ", validate=MailValidator()
        ).execute()

        if UtilisateurService().mail_deja_utilise(mail):
            from view.accueil.accueil_vue import AccueilVue
            return AccueilVue(f"L'adresse {mail} est déjà utilisée.")

        mdp = inquirer.secret(
            message="Entrez votre mot de passe : ",
            validate=PasswordValidator(
                length=8,
                cap=True,
                number=True,
                message="Au moins 8 caractères, incluant une majuscule et un chiffre",
            ),
        ).execute()

        naiss = inquirer.text(
            message="Entrez votre date de naissance (YYYY-MM-DD) : ",
            validate=EmptyInputValidator(),
        ).execute()

        # Appel du service pour créer l'utilisateur
        utilisateur = UtilisateurService().creer(prenom, nom, mdp, naiss, mail)

        # Si l'utilisateur a été créé
        if utilisateur:
            message = (
                f"Votre compte {utilisateur.prenom} {utilisateur.nom} "
                f"a été créé. Vous pouvez maintenant vous connecter."
            )
        else:
            message = "Erreur lors de la création de votre compte."

        from view.accueil.accueil_vue import AccueilVue
        return AccueilVue(message)


class MailValidator(Validator):
    """La classe MailValidator vérifie si la chaîne de caractères
    correspond au format d'un email valide."""

    def validate(self, document) -> None:
        ok = regex.match(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$", document.text)
        if not ok:
            raise ValidationError(
                message="Veuillez entrer une adresse email valide",
                cursor_position=len(document.text),
            )
