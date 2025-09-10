from dao.utilisateur_dao import UtilisateurDao
from business_object.utilisateur import Utilisateur

class UtilisateurService:
    def __init__(self):
        self.dao = UtilisateurDao()

    def profil(self, id_utilisateur: int) -> Utilisateur:
        return self.dao.find_by_id(id_utilisateur)

    def maj_profil(self, u: Utilisateur) -> Utilisateur:
        return self.dao.update(u)
