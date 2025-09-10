class Utilisateur:
    """
    Classe représentant un Utilisateur

    Attributs
    ----------
    id_utilisateur : int
        identifiant
    prenom : str
        prénom de l'utilisateur
    nom : str
        nom de l'utilisateur
    mdp : str
        le mot de passe de l'utilisateur
    naiss : str
        date de naissance (au format YYYY-MM-DD)
    mail : str
        adresse mail de l'utilisateur
    """

    def __init__(self, prenom, nom, naiss, mail, mdp_hash=None, id_utilisateur=None):
        """Constructeur"""
        self.id_utilisateur = id_utilisateur
        self.prenom = prenom
        self.nom = nom
        self.mdp_hash = mdp_hash
        self.naiss = naiss
        self.mail = mail

    def __str__(self):
        """Permet d'afficher les informations de l'utilisateur"""
        return f"Utilisateur({self.prenom} {self.nom}, né(e) le {self.naiss})"

    def as_list(self) -> list[str]:
        """Retourne les attributs de l'utilisateur dans une liste"""
        return [self.prenom, self.nom, self.naiss, self.mail]
