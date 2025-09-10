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
- **`init_db.py`** : création du schéma et des tables (utilisateur, personage, session, messages, settings).  
- **`pop_db.sql`** : jeu de données de démonstration (utilisateurs + personnages IA).  
- **`pop_db_test.sql`** : données isolées pour les tests DAO (schéma `projet_test_dao`).  

---

### **2. Dossier `doc/suivi`**
Notes et rendus hebdomadaires du projet.  
- **`2025.XX.XX-semaineX.md`** : avancées, blocages, décisions.

---

### **3. Dossier `logs`**
Fichiers de logs générés automatiquement.  
- **`my_application.log`** : trace des actions exécutées.

---

### **4. Dossier `src/business_object`**
Objets métiers représentant les entités du projet (dataclasses simples, sans logique technique).  
- **`utilisateur.py`** → `Utilisateur`  
- **`personage.py`** → `Personage`  
- **`chat.py`** → `ChatSession`, `ChatMessage`  
- **`settings.py`** → `UserSettings`

---

### **5. Dossier `src/dao`**
Accès aux données (Data Access Object, SQL uniquement).  
- **`db_connection.py`** → `DBConnection` (connexion PostgreSQL)  
- **`utilisateur_dao.py`** → `UtilisateurDao`  
- **`persona_dao.py`** → `PersonaDao`  
- **`chat_session_dao.py`** → `ChatSessionDao`  
- **`chat_message_dao.py`** → `ChatMessageDao`  
- **`settings_dao.py`** → `UserSettingsDao`

---

### **6. Dossier `src/service`**
Logique applicative (utilise les DAO, sans SQL direct).  
- **`auth_service.py`** → `AuthService` (connexion, inscription)  
- **`utilisateur_service.py`** → `UtilisateurService` (profil utilisateur)  
- **`persona_service.py`** → `PersonaService` (gestion des personnages IA)  
- **`chat_service.py`** → `ChatService` (nouvelle session, messages, export, suppression)  
- **`settings_service.py`** → `SettingsService` (préférences utilisateur)  
- **`search_service.py`** → `SearchService` (recherche dans l’historique)  
- **`stats_service.py`** → `StatsService` (statistiques utilisateur et usage IA)

---

### **7. Dossier `src/view`**
Interface CLI avec InquirerPy. Chaque vue **retourne** la vue suivante.  

- **`vue_abstraite.py`** → `VueAbstraite`  
- **`session.py`** → `Session` (utilisateur + session courante)  
- **`menu_utilisateur_vue.py`** → `MenuUtilisateurVue`  
- **`chatIA_new.py`** → `ChatNew` (chat avec l’API ensai-GPT)  
- **`historique_vue.py`** → `HistoriqueVue`  
- **`parametres_vue.py`** → `ParametresVue`  
- **`personas_vue.py`** → `PersonasVue`

Sous-dossier **`view/accueil`** :  
- **`accueil_vue.py`** → `AccueilVue` (menu initial : Se connecter, Créer un compte, etc.)  
- **`connexion_vue.py`** → `ConnexionVue` (connexion avec mail/mdp)  
- **`inscription_vue.py`** → `InscriptionVue` (création d’un compte utilisateur)

---

### **8. Dossier `src/ChatIA`**
Client API pour l’IA.  
- **`ia_client.py`** → `IAClient` (appel HTTP `POST /generate` à l’API ENSAI-GPT)

---

### **9. Dossier `src/utilisateur`**
Optionnel : peut contenir les vues liées uniquement au profil utilisateur.  
- **`profil_vue.py`** → affichage et modification du profil.  

---

### **10. Dossier `src/utils`**
Outils techniques transverses.  
- **`log_init.py`** : initialisation des logs  
- **`log_decorator.py`** : décorateur de traçage  
- **`reset_database.py`** : réinitialisation de la base  
- **`securite.py`** : gestion du hashage des mots de passe  
- **`singleton.py`** : pattern Singleton pour DB  
- **`validators.py`** : fonctions de validation (mails, titres…)  
- **`export.py`** : export d’une conversation (JSON, Markdown)

---

### **11. Dossier `src`**
Fichiers principaux de l’application.  
- **`main.py`** : application CLI (enchaîne les vues)  
- **`app.py`** : webservice FastAPI (routes REST : utilisateurs, sessions, messages, stats)

---

### **12. Dossier `tests`**
Tests unitaires avec Pytest.  
- **`test_dao/test_utilisateur_dao.py`**  
- **`test_service/test_chat_service.py`**  
- **`test_service/test_auth_service.py`**  
- **`conftest.py`** : fixtures (connexion test, nettoyage schéma)

---

### **13. Fichiers racine**
| Fichier                   | Description                                                                 |
| -------------------------- | --------------------------------------------------------------------------- |
| `.env`                     | Variables d’environnement (PostgreSQL + API IA).                           |
| `requirements.txt`         | Dépendances Python nécessaires.                                             |
| `logging_config.yml`       | Configuration YAML pour les logs.                                           |
| `.coveragerc`              | Configuration Coverage pour les tests.                                      |
| `.github/workflows/ci.yml` | Pipeline CI (tests, analyse pylint, build auto).                            |

---


## 🔁 **Flux typiques**

- **Connexion** : `ConnexionVue` → `AuthService.se_connecter()` → `UtilisateurDao.find_by_mail()` → mot de passe vérifié → retour `MenuUtilisateurVue`.  
- **Nouveau Chat** : `MenuUtilisateurVue` → `PersonasVue` → `ChatService.start_session()` → `ChatNew` → `IAClient.generate()` → `ChatMessageDao.append()`.  
- **Historique** : `HistoriqueVue` → `SearchService.search_messages()` → affichage → supprimer/télécharger via `ChatService`.  
- **Paramètres** : `ParametresVue` → `SettingsService.set_user_prefs()` (tokens, température, profil).  
- **Statistiques** : `StatsService` → nombre de chats, durée moyenne, personnages IA les plus utilisés.  

---



## **Préparer l’environnement virtuel**


### **1- Cloner le projet dans ton Datalab (VSCode-python).**

```python
git clone https://github.com/EnsaiGPT-Projet-grp13/ensai-gpt
````

### **2- Créer et activer un environnement virtuel :**
dans la racine du projet
```python
python -m venv .venv
source ~/work/ensai-gpt/.venv/bin/activate
````

### **3- Installer les dépendances :**

```python
pip install -r requirements.txt

````

## **Configurer la base de données**

Dans Onyxia, lance aussi un service PostgreSQL.
Un README est généré automatiquement avec tes informations de connexion.
Exemple :
POSTGRES_HOST=postgresql-753783.user-toto
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=user-toto
POSTGRES_PASSWORD=motdepassefourni
POSTGRES_SCHEMA=projetGPT

 Copie ces lignes dans un fichier .env à la racine du projet.

### **4- Initialiser la base**
 Crée le schéma et les tables :

```python
python data/init_db.py
````
Si tout est correct tu devrai voir,  Base/Schéma initialisés dans `projetGPT`

### **5- remplir la Base de données (quelques utilisateurs et quelques personnages IA)**

A VENIR 

### **6. Lancer l’application CLI**
Démarre l’interface en ligne de commande (menus, inscription, chat IA, etc.) :

```python
python src/main.py

````


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

yyy
---


