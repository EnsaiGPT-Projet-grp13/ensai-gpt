# **Projet Informatique 2A ENSAI – Application Utilisateurs & Chat IA**

## **Description**
Ce projet a été réalisé dans le cadre du cours de **Projet Informatique en 2ème année à l’ENSAI**.  
Il vise à mettre en pratique plusieurs concepts fondamentaux de l’ingénierie logicielle et des systèmes d’information :  
- l’architecture en couches (DAO, service, view, business_object)  
- la connexion à une base de données PostgreSQL  
- une interface en ligne de commande (CLI) avec [InquirerPy](https://inquirerpy.readthedocs.io/en/latest/)  
- l’appel à un webservice externe  
- la création d’un webservice avec FastAPI  

Un second aspect clé du projet est l’intégration d’un service de **chat IA** à partir de l’API :  
👉 [API ENSAI-GPT](https://ensai-gpt-109912438483.europe-west4.run.app/docs#/default/chat_generate_post)

---

## **Structure du Projet**

### **1. Dossier `data`**
Contient les scripts SQL permettant d’initialiser et de peupler la base de données.  

- **`init_db.sql`** : création des tables  
- **`pop_db.sql`** : données initiales de la base  
- **`pop_db_test.sql`** : données spécifiques aux tests unitaires  

### **2. Dossier `src/business_object`**
Contient les classes métiers représentant les objets du domaine.  
- `utilisateur.py` : définit la classe `Utilisateur` (attributs, méthodes, etc.)

### **3. Dossier `src/dao`**
Accès aux données (Data Access Object).  
- `db_connection.py` : gestion de la connexion PostgreSQL  
- `utilisateur_dao.py` : CRUD sur les utilisateurs  

### **4. Dossier `src/service`**
Logique applicative (entre la DAO et la vue).  
- `utilisateur_service.py` : gestion des règles métier liées aux utilisateurs  

### **5. Dossier `src/view`**
Interface en ligne de commande.  
- `vue_abstraite.py` : classe de base pour les vues  
- `accueil_vue.py` : menu d’accueil  
- `menu_utilisateur_vue.py` : menu principal utilisateur  
- `chat_ai_vue.py` : choix d’une personnalité IA  
- `chat_session_vue.py` : boucle de discussion avec l’IA  

### **6. Dossier `src/client`**
Clients vers des webservices externes.  
- `ia_client.py` : client HTTP vers l’API de Chat IA  

### **7. Dossier `src/personas`**
Gestion des personnalités de l’IA.  
- `persona.py` : structure de données d’un persona  
- `registry.py` : liste des personnalités disponibles (ex. docteur, philosophe, ami, etc.)  

### **8. Dossier `src/utils`**
Outils communs.  
- `reset_database.py` : réinitialisation du schéma et des données  
- `securite.py` : hashage des mots de passe  
- `singleton.py`, `log_decorator.py`, `log_init.py` : design patterns et logs  

### **9. Dossier `tests`**
Tests unitaires du projet (pytest).  
- `test_utilisateur_dao.py`  
- `test_utilisateur_service.py`

### **10. Autres fichiers**
| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `.github/workflows/ci.yml` | Pipeline CI (tests + linting avec pylint)                                 |
| `.vscode/settings.json`    | Paramètres de développement VS Code                                      |
| `.env`                     | Variables d’environnement (BDD + webservice)                             |
| `requirements.txt`         | Dépendances Python nécessaires                                           |

---

## **Installation**
Clonez ce repository et installez les dépendances :  

```bash
pip install -r requirements.txt
pip list
