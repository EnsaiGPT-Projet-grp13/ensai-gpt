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
Contient les scripts SQL et utilitaires de base de données.
- `init_db.py` → création du schéma et des tables (utilisateur, personnage, session, messages, settings).
- `pop_db.py` → jeu de données de démonstration (utilisateurs + personnages IA

### Dossier `src`
Contient tout le code source de l’application.

#### `src/objects`
Entités (dataclasses)

- `utilisateur.py` → `class User`
- `utilisateur_session.py` → `class UserSession`
- `settings.py` → `class UserSettings`
- `persona.py` → `class Persona`
- `conversation.py` → `class Conversation`
- `message.py` → `class ChatMessage`

#### `src/dao`
Accès **pur** base de données, via une connexion unique.

- `db.py` → `DB`
  - connexion unique (singleton), curseur, helpers transaction (begin/commit/rollback)

- `utilisateur_dao.py` → `UserDao` (find_by_email, create, update_email, get_password_hash, update_password_hash)

- `utilisateur_session_dao.py` → `UserSessionDao` (start, end)

- `settings_dao.py` → `SettingsDao` (get, upsert)

- `persona_dao.py` → `PersonaDao` (list_for_user, list_public, insert, update, get)

- `conversation_dao.py` → `ConversationDao` (insert, save_toke, update_title, get, delete, search_by_user_and_title, maj prompt, get_by_token)

- `message_dao.py` → `MessageDao` (save                        *(user/assistant/system), list, history, fts_search)
  
- `stats_dao.py` → `StatsDao` (messages_count_by_user, conversations_count_by_user, session_durations)

#### `src/service`
Communication avec l'API.

- `auth_service.py` → `AuthService` (login, register, update email, change password)

- `session_service.py` → `SessionService` (start / end)

- `settings_service.py` → `SettingsService` (get defaults / update defaults (température))

- `persona_service.py` → `PersonaService` (list (public + mes personas), create / update / get)
  
- `utilisateur_service.py` → `UtilisateurService` (list, create, update, get)

- `conversation_service.py` → `ConversationService` (create (snapshot + token si public), join by token, rename title / change persona (met à jour le snapshot), delete / list (historique), get snapshot)

- `message_service.py` → `MessageService` (list messages, save user message + generate reply (appelle l’IA))

- `search_service.py` → `SearchService` (search in conversation)

- `export_service.py` → `ExportService` (export conversation)

- `stats_service.py` → `StatsService` a voir


### `src/view`
Interface CLI (menus). Chaque vue a surtout **`run()`** et délègue aux services.

**Menus**
- `vue_abstraite.py` → `VueAbstraite` (helpers UI de base)
- `accueil_vue.py` → `AccueilVue` (menu: Connexion / Inscription / Chat rapide / Quitter)
- `connexion_vue.py` → `ConnexionVue` (email+mdp → login)
- `inscription_vue.py` → `InscriptionVue` (création de compte)
- `menu_utilisateur_vue.py` → `MenuUtilisateurVue` (après login : Chat / Historique / Paramètres / Déconnexion)

**Chat**
- `chat_menu_vue.py` → `MenuChatVue` (Rejoindre via token / Nouvelle conversation / Historique / Chat rapide)
- `token_join_vue.py` → `TokenJoinVue` (saisir token → rejoindre conv)
- `nouvelle_conversation_vue.py` → `NouvelleConversationVue` (choisir persona → privé/public(+token) → titre → ouvre le chat)
- `chat_rapide_vue.py` → `ChatRapideVue` (conv privée immédiate, prompt par défaut)
- `reponse_ia_vue.py` → `ReponseIAVue` (boucle chat : envoyer → générer réponse)

**Historique & Paramètres**
- `historique_vue.py` → `HistoriqueVue` (lister/rechercher par titre, ouvrir/renommer/changer persona/supprimer/exporter)
- `parametres_vue.py` → `ParametresVue` (Compte / Préférences / Personas)
- `parametres_compte_vue.py` → `ParametresCompteVue` (changer email/mdp)
- `preferences_vue.py` → `PreferencesVue` (température par défaut)
- `personas_vue.py` → `PersonasVue` (lister / créer / éditer / supprimer)
- `stats_vue.py` → `StatsVue` (quelques stats utilisateur)


#### `src` (fichiers racine)
Points d’entrées.
- `main.py` → lance le **CLI** (enchaîne les vues)
- `app.py` → instancie **FastAPI** + inclut `api/router.py`

### Dossier `tests`
Unit tests **pytest** (à minima).
- `test_dao/test_user_dao.py`, `test_dao/test_persona_dao.py`, `test_dao/test_conversation_dao.py`, `test_dao/test_message_dao.py`, `test_dao/test_settings_dao.py`
- `test_service/test_auth_service.py`, `test_service/test_conversation_service.py`, `test_service/test_message_service.py`, `test_service/test_stats_service.py`
- `conftest.py` → fixtures (DB tests)...

### Dossier `doc`
- `doc/suivi/` (hebdo), `doc/diagrammes/` (Mermaid), `doc/logs/`
- `README_DOC.md`

## Fichiers racine
- `.env` (PostgreSQL + URL API ENSAI-GPT + paramètres pars défaut)
- `requirements.txt` (FastAPI, psycopg, pydantic, InquirerPy, etc.)
- `logging_config.yml`, `.coveragerc`, `.github/workflows/ci.yml`
- `LICENSE`, `README.md`

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

### **5(facultatif)- Remplir la Base de données (quelques utilisateurs et quelques personnages IA)**

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



