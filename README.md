# **Projet Informatique 2A ENSAI – Application Utilisateurs & Chat IA**

## **Description**
Ce projet est réalisé dans le cadre du **Projet Informatique de 2ème année à l’ENSAI**.  
Il met en œuvre une architecture en couches (DAO, service, view, business_object), une base de données PostgreSQL, une interface en ligne de commande avec InquirerPy, et un webservice construit avec FastAPI.  
Un module de **Chat IA** est intégré grâce à l’API :  
👉 [API ENSAI-GPT](https://ensai-gpt-109912438483.europe-west4.run.app/docs#/default/chat_generate_post)

---

## **Objectifs**
- Développer un assistant conversationnel ensaiGPT où chaque utilisateur peut se connecter et discuter avec une IA.

- Permettre la personnalisation de l’agent (ton, style, niveau de détail, humour/professionnalisme).

- Offrir un carnet de bord interactif pour retrouver l’historique des conversations. 

---

## **Structure du Projet**

### **1. Dossier `data`**
Contient les scripts SQL de gestion de la base.  
- **`init_db.sql`** : création des tables.  
- **`pop_db.sql`** : insertion des données principales.  
- **`pop_db_test.sql`** : données spécifiques aux tests unitaires.  

### **2. Dossier `doc/suivi`**
Notes et rendus hebdomadaires du projet.  
- **`2025.09.04-semaine1.md`** : suivi de la première semaine.  

### **3. Dossier `logs`**
Fichiers de logs générés automatiquement.  
- **`my_application.log`** : trace des actions exécutées.  

### **4. Dossier `src/business_object`**
Objets métiers représentant les entités du projet.  
- **`utilisateur.py`** : classe `Utilisateur` avec ses attributs et méthodes.  

### **5. Dossier `src/dao`**
Accès aux données (Data Access Object).  
- **`db_connection.py`** : gestion de la connexion PostgreSQL.  
- **`utilisateur_dao.py`** : CRUD complet sur les utilisateurs.  

### **6. Dossier `src/service`**
Logique applicative entre DAO et vues.  
- **`utilisateur_service.py`** : création, authentification, modification et suppression des utilisateurs.  

### **7. Dossier `src/view`**
Interface CLI avec InquirerPy.  
- **`accueil_vue.py`** : menu d’accueil.  
- **`connexion_vue.py`** : vue de connexion.  
- **`inscription_vue.py`** : vue d’inscription.  
- **`menu_utilisateur_vue.py`** : menu principal utilisateur.  
- **`session.py`** : gestion de la session courante.  
- **`vue_abstraite.py`** : classe de base pour les vues.  

### **8. Dossier `src/ChatIA`**
Gestion du module de Chat IA.  
- **`ia_client.py`** (à créer) : client HTTP vers l’API IA. 

### **9. Dossier `src/utilisateur`**
Client pour manipuler les utilisateurs depuis l’extérieur.  
- **`utilisateur_client.py`** : appels à l’API côté utilisateur.  

### **10. Dossier `src/utils`**
Outils techniques transverses.  
- **`log_init.py`** : configuration des logs.  
- **`log_decorator.py`** : décorateur pour tracer entrées/sorties.  
- **`reset_database.py`** : réinitialisation de la base.  
- **`securite.py`** : gestion du hash des mots de passe.  
- **`singleton.py`** : implémentation du pattern Singleton.  

### **11. Dossier `src`**
Fichiers principaux de l’application.  
- **`main.py`** : lance l’application CLI.  
- **`app.py`** : lance le webservice FastAPI.  

### **12. Dossier `tests`**
Tests unitaires avec Pytest.  
- **`test_dao/test_utilisateur_dao.py`** : tests sur la DAO.  
- **`test_service/test_utilisateur_service.py`** : tests sur la logique métier.  

### **13. Fichiers racine**
| Fichier                   | Description                                                                 |
| -------------------------- | --------------------------------------------------------------------------- |
| `.env`                     | Variables d’environnement (PostgreSQL + API IA).                           |
| `requirements.txt`         | Dépendances Python nécessaires.                                             |
| `logging_config.yml`       | Configuration YAML pour les logs.                                           |
| `.coveragerc`              | Configuration Coverage pour les tests.                                      |
| `.github/workflows/ci.yml` | Pipeline CI : tests, analyse avec pylint, build automatique.                 |

---


## **:arrow_forward: Variables d’environnement**
Créer un fichier `.env` à la racine et y ajouter :  

```default
WEBSERVICE_HOST=https://ensai-gpt-109912438483.europe-west4.run.app

POSTGRES_HOST=sgbd-eleves.domensai.ecole
POSTGRES_PORT=5432
POSTGRES_DATABASE=idxxxx
POSTGRES_USER=idxxxx
POSTGRES_PASSWORD=idxxxx
POSTGRES_SCHEMA=projet


---

## **:arrow_forward: Lancer l’application CLI**
python src/main.py

- Menu interactif avec InquirerPy.  
- Permet l’inscription, la connexion et l’accès au Chat IA.  

---

## **:arrow_forward: Lancer le webservice**
python src/app.py


Documentation interactive :  
- [http://localhost:9876/docs](http://localhost:9876/docs)  
- [http://localhost:9876/redoc](http://localhost:9876/redoc)  

Endpoints principaux :  
- `GET /utilisateur`  
- `GET /utilisateur/{id}`  
- `POST /utilisateur/`  
- `PUT /utilisateur/{id}`  
- `DELETE /utilisateur/{id}`  

---

## **:arrow_forward: Tests unitaires**
Exécuter :  

pytest -v


Les tests DAO utilisent le schéma `projet_test_dao` et les données `pop_db_test.sql`.  

### Couverture des tests
Il est possible de générer un rapport de couverture avec :  

coverage run -m pytest
coverage report -m
coverage html


➡️ Ouvrir `coverage_report/index.html` pour un rapport détaillé.  

---

## **:arrow_forward: Logs**
- Configurés via `src/utils/log_init.py` et `logging_config.yml`.  
- Stockés dans `logs/my_application.log`.  

Exemple de log :  

07/08/2024 09:07:07 - INFO - ConnexionVue
07/08/2024 09:07:08 - INFO - utilisateurService.se_connecter('a', '') - DEBUT
07/08/2024 09:07:08 - INFO - utilisateurDao.se_connecter('a', '') - DEBUT
07/08/2024 09:07:08 - INFO - utilisateurDao.se_connecter('a', '*****') - FIN
07/08/2024 09:07:08 - INFO - └─> Sortie : utilisateur(a, 20 ans)


---


