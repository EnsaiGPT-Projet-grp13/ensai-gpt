# **Projet Informatique 2A ENSAI – EnsaiGPT (Grp13)**

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
### Dossier `data`
Contient les scripts SQL de gestion de la base.  
- **`init_db.py`** : création du schéma et des tables (utilisateur, personage, session, messages, settings).  
- **`pop_db.py`** : jeu de données de démonstration (utilisateurs + personnages IA).  
- **`test_api.py`** : tests appel API.  


### Dossier `src`  
Contient tout le code source de l’application (logique métier, DAO, services, vues, utilitaires).

#### src/business_object  
Définit les objets métiers (entités simples, sans logique technique).  

- **`utilisateur.py`** → classe `Utilisateur`  
- **`personageIA.py`** → classe `PersonageIA`  
- **`chat.py`** → classes `ChatSession`, `ChatMessage`  
- **`settings.py`** → classe `UserSettings`

#### src/dao  
Gère l’accès à la base de données (requêtes SQL, connexions, DAO).  

- **`db_connection.py`** → classe `DBConnection` (connexion PostgreSQL)  
- **`utilisateur_dao.py`** → `UtilisateurDao` (CRUD utilisateurs)  
- **`persona_dao.py`** → `PersonaDao` (CRUD personnages IA)  
- **`chat_session_dao.py`** → `ChatSessionDao`  
- **`chat_message_dao.py`** → `ChatMessageDao`  
- **`settings_dao.py`** → `UserSettingsDao`

#### src/service  
Implémente la logique applicative (utilise les DAO, pas de SQL direct).  

- **`auth_service.py`** → `AuthService` (connexion, inscription)  
- **`utilisateur_service.py`** → `UtilisateurService` (profil)  
- **`persona_service.py`** → `PersonaService` (personnages IA)  
- **`chat_service.py`** → `ChatService` (sessions de chat, messages)  
- **`settings_service.py`** → `SettingsService` (préférences utilisateur)  
- **`search_service.py`** → `SearchService` (recherche historique)  
- **`stats_service.py`** → `StatsService` (statistiques)

#### src/view  
Interface CLI (menus interactifs avec InquirerPy).  
Chaque vue affiche et retourne la vue suivante.  

- **`vue_abstraite.py`** → classe de base `VueAbstraite`  
- **`session.py`** → `Session` (utilisateur + session courante)  
- **`accueil_vue.py`** → `AccueilVue` (menu principal : connexion, inscription, reset)  
- **`connexion_vue.py`** → `ConnexionVue` (authentification)  
- **`inscription_vue.py`** → `InscriptionVue` (création compte)  
- **`menu_utilisateur_vue.py`** → `MenuUtilisateurVue` (après connexion)  
- **`reponseIA_vue.py`** → `ReponseIAVue` (chat avec ensai-GPT)  
- **`historique_vue.py`** → `HistoriqueVue` (liste conversations passées)  
- **`parametres_vue.py`** → `ParametresVue` (modifier préférences)  
- **`personages_vue.py`** → `PersonasVue` (choisir/créer un personnage IA)

#### src/utils  
Outils techniques et fonctions transverses.  

- **`log_init.py`** → initialisation des logs  
- **`log_decorator.py`** → décorateur pour tracer les appels  
- **`reset_database.py`** → réinitialisation de la base  
- **`securite.py`** → hashage et vérification mots de passe  
- **`singleton.py`** → pattern Singleton (connexion DB)  
- **`ia_client.py`** → `IAClient` (appels API `POST /generate` à ensai-GPT)

#### src (fichiers racine)  
Point d’entrée de l’application et webservice.  

- **`main.py`** → lance l’application CLI (enchaîne les vues)  
- **`app.py`** → webservice FastAPI (routes REST : utilisateurs, sessions, messages, stats)

### Dossier `tests`
Tests unitaires avec Pytest.  
- **`test_dao/test_utilisateur_dao.py`**  
- **`test_service/test_chat_service.py`**  
- **`test_service/test_auth_service.py`**  
- **`conftest.py`** : fixtures (connexion test, nettoyage schéma)


### Dossier `doc`

#### doc/suivi
Notes et rendus hebdomadaires du projet.  
- **`2025.XX.XX-semaineX.md`** : avancées, blocages, décisions.

### doc/logs
Fichiers de logs générés automatiquement.  
- **`my_application.log`** : trace des actions exécutées.

### doc/digrammes
Diagrammes d'organisation denotre projet

### Fichiers racine
| Fichier                   | Description                                                                 |
| -------------------------- | --------------------------------------------------------------------------- |
| `.env`                     | Variables d’environnement (PostgreSQL + API IA).                           |
| `requirements.txt`         | Dépendances Python nécessaires.                                             |
| `logging_config.yml`       | Configuration YAML pour les logs.                                           |
| `.coveragerc`              | Configuration Coverage pour les tests.                                      |
| `.github/workflows/ci.yml` | Pipeline CI (tests, analyse pylint, build auto).                            |

---


## **Préparer l’environnement virtuel**

### **0- Initialiser l'environnement.**

Sur oxyxia (ou SSPCloud) : lancer VScode, lancer PostGreSQL, lancer CloudBeaver

### **1- Cloner le projet dans ton Datalab (VSCode-python).**

```python
git clone https://github.com/EnsaiGPT-Projet-grp13/ensai-gpt
````

### **2- Créer et activer un environnement virtuel :**

Dans la racine du projet :

```python
cd ensai-gpt/
python -m venv .venv
source ~/work/ensai-gpt/.venv/bin/activate
````

### **3- Installer les dépendances :**

```python
pip install -r requirements.txt

````

## **Configurer la base de données**

 Créer un fichier .env et copier les lignes suivantes :

```python
WEBSERVICE_HOST=https://ensai-gpt-109912438483.europe-west4.run.app
LLM_TEMPERATURE=0.7
LLM_TOP_P=1.0
LLM_MAX_TOKENS=300

POSTGRES_HOST=           # ⚠️ à remplacer par votre host
POSTGRES_PORT=5432
POSTGRES_DATABASE=       # ⚠️ à remplacer par votre db
POSTGRES_USER=           # ⚠️ à remplacer par votre identifiant
POSTGRES_PASSWORD=       # ⚠️ à remplacer par votre mot de passe
POSTGRES_SCHEMA=projetGPT
````


### **4- Initialiser la base**

 Crée le schéma et les tables :

```python
python data/init_db.py
````
Si tout est correct tu devrai voir,  "Base/Schéma initialisés dans `projetGPT`"

### **5(facultatif)- remplir la Base de données (quelques utilisateurs et quelques personnages IA)**

```python
python data/pop_db.py
````

### **6. Lancer l’application**

Démarre l’interface en ligne de commande :

```python
python src/main.py
````

---

## **Tests unitaires**

Exécuter :  

```python
pytest -v
````


### Couverture des tests
Il est possible de générer un rapport de couverture avec :  

coverage run -m pytest
coverage report -m
coverage html


-> Ouvrir `coverage_report/index.html` pour un rapport détaillé.  

---

## Logs**
- Configurés via `src/utils/log_init.py` et `logging_config.yml`.  
- Stockés dans `logs/my_application.log`.  

Exemple de log :  

07/08/2024 09:07:07 - INFO - ConnexionVue
07/08/2024 09:07:08 - INFO - utilisateurService.se_connecter('a', '') - DEBUT
07/08/2024 09:07:08 - INFO - utilisateurDao.se_connecter('a', '') - DEBUT
07/08/2024 09:07:08 - INFO - utilisateurDao.se_connecter('a', '*****') - FIN
07/08/2024 09:07:08 - INFO - └─> Sortie : utilisateur(a, 20 ans)

---


