import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src.service.utilisateur_service import UtilisateurService
from src.utils.log_init import initialiser_logs

app = FastAPI(title="Mon webservice (Utilisateurs)")

initialiser_logs("Webservice")

utilisateur_service = UtilisateurService()


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/utilisateur/", tags=["Utilisateurs"])
async def lister_tous_utilisateurs():
    """Lister tous les utilisateurs (mdp masqués par défaut côté service)"""
    logging.info("Lister tous les utilisateurs")
    liste = utilisateur_service.lister_tous()

    liste_model = []
    for u in liste:
        liste_model.append(u)

    return liste_model


@app.get("/utilisateur/{id_utilisateur}", tags=["Utilisateurs"])
async def utilisateur_par_id(id_utilisateur: int):
    """Trouver un utilisateur à partir de son id"""
    logging.info("Trouver un utilisateur à partir de son id")
    utilisateur = utilisateur_service.trouver_par_id(id_utilisateur)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur


class UtilisateurModel(BaseModel):
    """Modèle Pydantic pour les Utilisateurs"""
    id_utilisateur: int | None = None
    prenom: str
    nom: str
    mdp: str
    naiss: str   # au format 'YYYY-MM-DD' (ou utiliser date si tu préfères)
    mail: str


@app.post("/utilisateur/", tags=["Utilisateurs"])
async def creer_utilisateur(u: UtilisateurModel):
    """Créer un utilisateur"""
    logging.info("Créer un utilisateur")
    if utilisateur_service.mail_deja_utilise(u.mail):
        raise HTTPException(status_code=404, detail="Mail déjà utilisé")

    utilisateur = utilisateur_service.creer(u.prenom, u.nom, u.mdp, u.naiss, u.mail)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Erreur lors de la création de l'utilisateur")

    return utilisateur


@app.put("/utilisateur/{id_utilisateur}", tags=["Utilisateurs"])
def modifier_utilisateur(id_utilisateur: int, u: UtilisateurModel):
    """Modifier un utilisateur"""
    logging.info("Modifier un utilisateur")
    utilisateur = utilisateur_service.trouver_par_id(id_utilisateur)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    utilisateur.prenom = u.prenom
    utilisateur.nom = u.nom
    utilisateur.mdp = u.mdp
    utilisateur.naiss = u.naiss
    utilisateur.mail = u.mail

    utilisateur = utilisateur_service.modifier(utilisateur)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Erreur lors de la modification de l'utilisateur")

    return f"Utilisateur {u.prenom} {u.nom} modifié"


@app.delete("/utilisateur/{id_utilisateur}", tags=["Utilisateurs"])
def supprimer_utilisateur(id_utilisateur: int):
    """Supprimer un utilisateur"""
    logging.info("Supprimer un utilisateur")
    utilisateur = utilisateur_service.trouver_par_id(id_utilisateur)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    utilisateur_service.supprimer(utilisateur)
    return f"Utilisateur {utilisateur.prenom} {utilisateur.nom} supprimé"


@app.get("/hello/{name}")
async def hello_name(name: str):
    """Afficher Hello"""
    logging.info("Afficher Hello")
    return f"message : Hello {name}"


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9876)

    logging.info("Arret du Webservice")
