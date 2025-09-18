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

## Dossier `data`
Contient les scripts SQL et utilitaires de base de données.
- `init_db.py` → création du schéma et des tables (utilisateur, personnage, session, messages, settings).
- `pop_db.py` → jeu de données de démonstration (utilisateurs + personnages IA).
- `sql/schema.sql` → script SQL du schéma (optionnel si tu préfères tout en Python).
- `sql/seed.sql` → données de seed (optionnel).

---
## Dossier `src`
Contient tout le code source de l’application, réorganisé selon **api/**, **dao/**, **objects/**, **service/**, **view/**, avec **main.py** (CLI) et **app.py** (FastAPI).

---

### `src/objects`
Entités (dataclasses) et schémas API (Pydantic). **Pas de logique** ici.
- `user.py` → `class User`
- `user_session.py` → `class UserSession`
- `settings.py` → `class UserSettings`
- `persona.py` → `class Persona`
- `conversation.py` → `class Conversation`
- `message.py` → `class ChatMessage`
- `schemas.py` → Pydantic DTO
  - `class LoginIn`, `class RegisterIn`
  - `class ConversationCreateIn`, `class ConversationRenameIn`, `class ConversationPersonaIn`
  - `class MessageIn`
  - `class PersonaIn`, `class PersonaUpdateIn`
  - `class UserSettingsIn`, `class UpdateEmailIn`, `class UpdatePasswordIn`

---

### `src/dao`
Accès **pur** base de données (SQL/CRUD), via une connexion unique.
- `db.py`
  - `class DB` → `connection()`, helpers transaction
- `user_dao.py`
  - `class UserDao` → `find_by_email(email)`, `create(email, hash, display_name)`, `update_email(user_id, new_email)`, `get_password_hash(user_id)`, `update_password_hash(user_id, new_hash)`
- `user_session_dao.py`
  - `class UserSessionDao` → `start(user_id, ip, ua)`, `end(session_id)`
- `settings_dao.py`
  - `class SettingsDao` → `get(user_id)`, `upsert(user_id, **kwargs)`
- `persona_dao.py`
  - `class PersonaDao` → `list_for_user(user_id)`, `list_public()`, `insert(owner_user_id|None, name, system_prompt, **params)`, `update(persona_id, **fields)`, `get(persona_id)`
- `conversation_dao.py`
  - `class ConversationDao` →  
    `insert(owner_user_id, snapshot_system|None, **params)`,  
    `save_token(conversation_id, token, is_public)`,  
    `update_title(conversation_id, title)`,  
    `get(conversation_id)`, `get_snapshot(conversation_id)`,  
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

---

### `src/service`
Logique applicative (orchestration, règles métier). **Aucun SQL direct**.
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

---

### `src/api`
Routes **FastAPI** (validation I/O, délègue au *service*).
- `router.py` → compose tous les routers (tags/prefix)
- `auth_api.py`
  - `POST /auth/login` → `login(payload: LoginIn)`
  - `POST /auth/register` → `register(payload: RegisterIn)`
  - `POST /auth/logout` → `logout(session_id: str)`
- `conversations_api.py`
  - `POST /conversations` → `create_conversation(payload: ConversationCreateIn)` *(snapshot + token si public)*
  - `POST /conversations/join` → `join_by_token(token: str)` *(collaboratif)*
  - `GET  /conversations/{id}` → `get_conversation(id: str)` *(messages via messages_api ou direct list)*
  - `PATCH /conversations/{id}/title` → `rename(id: str, payload: ConversationRenameIn)`
  - `PATCH /conversations/{id}/persona` → `change_persona(id: str, payload: ConversationPersonaIn)` *(snapshot MAJ)*
  - `GET  /conversations/{id}/search` → `search_in_conversation(id: str, q: str)`
  - `DELETE /conversations/{id}` → `delete_conversation(id: str)`
- `messages_api.py`
  - `POST /messages` → `post_user_message(payload: MessageIn)` *(save user msg → generate reply)*
  - `GET  /messages/{conversation_id}` → `list_messages(conversation_id: str)`
- `history_api.py`
  - `GET /history` → `list_history(title_query: str|None)` *(liste des conversations d’un user)*
- `personas_api.py`
  - `GET  /personas` → `list_personas()`
  - `POST /personas` → `create_persona(payload: PersonaIn)`
  - `PATCH /personas/{id}` → `update_persona(id: str, payload: PersonaUpdateIn)`
- `settings_api.py`
  - `GET  /settings` → `get_user_settings()`
  - `PATCH /settings/user` → `update_user_settings(payload: UserSettingsIn)` *(temp/top_p/max_tokens/style)*
  - `PATCH /settings/account/email` → `update_email(payload: UpdateEmailIn)`
  - `PATCH /settings/account/password` → `update_password(payload: UpdatePasswordIn)`
- `export_api.py`
  - `GET /export/conversation/{id}` → `export_conversation(id: str, fmt="json")`
- `stats_api.py`
  - `GET /stats/me` → `my_stats()`

---

### `src/view` (CLI InquirerPy)
Interface utilisateur (menus). **Appelle l’API**, jamais les DAO.
- `base.py` → `class VueAbstraite` *(helpers menu / navigation)*
- `session_ctx.py` → `class Session` *(user_id, session_id, persona selection, conversation courante)*
- `accueil.py` → `class AccueilVue` *(menu: Connexion, Inscription, Quitter)* → `run()`
- `connexion.py` → `class ConnexionVue` *(email+mdp → /auth/login)* → `run()`
- `inscription.py` → `class InscriptionVue` → `run()`
- `chat_hub.py` → `class ChatHubVue` *(**Rejoindre via token**, **Historique**, **Nouvelle conversation**)* → `run()`
  - `prompt_token()`, `go_historique()`, `go_new_conversation()`
- `personas.py` → `class PersonasVue` *(lister/créer/éditer)* → `run()`
- `reponse_ia.py` → `class ReponseIAVue` *(boucle chat)* → `run()`
  - `send_user_message()`, `show_assistant_reply()`
- `historique.py` → `class HistoriqueVue` *(lister/rechercher par titre, **ouvrir**, **supprimer**, **exporter**, **renommer**, **changer persona**, **recherche interne**)* → `run()`
- `parametres.py` → `class ParametresVue` *(compte email/mdp + préférences + édition personas)* → `run()`

---

### `src` (fichiers racine)
Points d’entrées.
- `main.py` → lance le **CLI** (enchaîne les vues)
- `app.py` → instancie **FastAPI** + inclut `api/router.py`

---

## Dossier `tests`
Unit tests **pytest** (à minima).
- `test_dao/test_user_dao.py`, `test_dao/test_persona_dao.py`, `test_dao/test_conversation_dao.py`, `test_dao/test_message_dao.py`, `test_dao/test_settings_dao.py`
- `test_service/test_auth_service.py`, `test_service/test_conversation_service.py`, `test_service/test_message_service.py`, `test_service/test_stats_service.py`
- `conftest.py` → fixtures (DB test, nettoyage schéma)

---

## Dossier `doc`
- `doc/suivi/` (hebdo), `doc/diagrammes/` (Mermaid), `doc/logs/`
- `README_DOC.md` (install, décisions d’archi)

---

## Fichiers racine
- `.env` (PostgreSQL + URL API ENSAI-GPT + params défaut)
- `requirements.txt` (FastAPI, psycopg, pydantic, InquirerPy, etc.)
- `logging_config.yml`, `.coveragerc`, `.github/workflows/ci.yml`
- `LICENSE`, `README.md`



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


