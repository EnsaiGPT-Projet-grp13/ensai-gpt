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

- `user.py` → `class User`
- `user_session.py` → `class UserSession`
- `settings.py` → `class UserSettings`
- `persona.py` → `class Persona`
- `conversation.py` → `class Conversation`
- `message.py` → `class ChatMessage`

#### `src/dao`
Accès **pur** base de données, via une connexion unique.
- `db.py`
  - `class DB` → `DBConnection()`
- `user_dao.py`
  - `class UserDao` → `find_by_email(email)`, `create(email, hash, display_name)`, `update_email(user_id, new_email)`, `get_password_hash(user_id)`, `update_password_hash(user_id, new_hash)`
- `user_session_dao.py`
  - `class UserSessionDao` → `start(user_id, ip, ua)`, `end(session_id)`
- `settings_dao.py`
  - `class SettingsDao` → `get(user_id)`, `upsert(user_id, **kwargs)`
- `persona_dao.py`
  - `class PersonaDao` → `list_for_user(user_id)`, `list_public()`, `insert(name, temperature, prompt)`, `update(persona_id, **fields)`, `get(persona_id)`
- `conversation_dao.py`
  - `class ConversationDao` →  
    `insert(owner_user_id,  **params)`,  
    `save_token(conversation_id, token, is_public)`,  
    `update_title(conversation_id, title)`,  
    `get(conversation_id)`, 
    `delete(conversation_id)`,  
    `search_by_user_and_title(user_id, query|None)`,  
    `change_snapshot_persona(conversation_id, persona_prompt, **params)`,  
    `get_by_token(token)`
- `conversation_member_dao.py`
  - `class ConversationMemberDao` → `add_member(conversation_id, user_id, role="collaborator")`
- `message_dao.py`
  - `class MessageDao` → `save(conversation_id, role, content, author_user_id|None)`, `list(conversation_id)`, `history_for_llm(conversation_id)`, `fts_search(conversation_id, q)`
- `stats_dao.py`
  - `class StatsDao` → `messages_count_by_user(user_id)`, `conversations_count_by_user(user_id)`, `session_durations(user_id)`

#### `src/service`
Communication avec l'API.

- `auth_service.py`
  - `class AuthService` → `login(email, password, ip, ua) -> (user_id, session_id)`, `register(email, password, display_name) -> user_id`, `update_email(user_id, new_email)`, `change_password(user_id, old_pwd, new_pwd)`
- `session_service.py`
  - `class SessionService` → `start(user_id, ip, ua) -> session_id`, `end(session_id)`
- `settings_service.py`
  - `class SettingsService` → `get_user_settings(user_id)`, `upsert_user_settings(user_id, **payload)`
- `persona_service.py`
  - `class PersonaService` → `list_personas(user_id)`, `create_persona(user_id, name, system_prompt, **params) -> persona_id`, `update_persona(user_id, persona_id, **payload)`, `get_persona(persona_id)`
- `conversation_service.py`
  - `class ConversationService` →  
    `create_conversation(user_id, persona_id|None, custom_system|None, temperature|None, top_p|None, max_tokens|None, visibility) -> dict{id, token?}`,  
    `join_by_token(user_id, token) -> conversation_id`,  
    `update_title(conversation_id, title)`,  
    `change_persona(conversation_id, persona_id)`,  
    `get_snapshot(conversation_id)`,  
    `delete_conversation(user_id, conversation_id)`,  
    `list_conversations(user_id, title_query|None)`
- `message_service.py`
  - `class MessageService` → `save_user_message(conversation_id, content, author_user_id)`, `generate_reply(conversation_id) -> assistant_content`, `list_messages(conversation_id)`
- `search_service.py`
  - `class SearchService` → `search_in_conversation(conversation_id, q)`
- `export_service.py`
  - `class ExportService` → `export_conversation(conversation_id, fmt) -> bytes`  *(fmt: json/csv/txt)*
- `stats_service.py`
  - `class StatsService` → `user_dashboard(user_id) -> dict`
- `clients/ia_client.py`
  - `generate(history: list[dict], temperature|None, top_p|None, max_tokens|None) -> str`  *(POST `/generate`)*
- `clients/security.py`
  - `hash_password(plain) -> str`, `verify_password(plain, hashed) -> bool`

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



