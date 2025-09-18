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
Contient tout le code source de l’application (logique métier, DAO, services, vues, utilitaires).

### `src/business_object`
Objets métiers (entités simples, sans logique technique).
- `utilisateur.py` → classe **Utilisateur**
- `personnage_ia.py` → classe **PersonnageIA** (prof, cuisinier, jardinier, …)
- `chat.py` → **ChatSession**, **ChatMessage**
- `settings.py` → **UserSettings** (température, style, top_p, max_tokens)
- `stats.py` → objets/statuts pour les statistiques utilisateur

### `src/dao`
Accès à la base (requêtes SQL, connexions, DAO).
- `db_connection.py` → **DBConnection** (connexion PostgreSQL, pattern Singleton)
- `utilisateur_dao.py` → **UtilisateurDao** (CRUD utilisateurs)
- `personnage_dao.py` → **PersonnageDao** (CRUD personnages IA, publics/privés)
- `chat_session_dao.py` → **ChatSessionDao** (CRUD sessions)
- `chat_message_dao.py` → **ChatMessageDao** (CRUD messages)
- `settings_dao.py` → **UserSettingsDao** (CRUD préférences)
- `stats_dao.py` → **StatsDao** (requêtes d’agrégats pour stats)

### `src/service`
Logique applicative (utilise les DAO, pas de SQL direct).
- `auth_service.py` → **AuthService** (connexion, inscription, vérifs)
- `utilisateur_service.py` → **UtilisateurService** (profil)
- `personnage_service.py` → **PersonnageService** (CRUD + listing public/privé)
- `chat_service.py` → **ChatService** (sessions, historique, appel IA)
- `settings_service.py` → **SettingsService** (upsert préférences, snapshot)
- `search_service.py` → **SearchService** (recherche dans l’historique)
- `stats_service.py` → **StatsService** (statistiques utilisateurs/globales)
- `export_service.py` → **ExportService** (export CSV/PDF du carnet de bord)

### `src/view`
Interface CLI (menus interactifs avec **InquirerPy**). Chaque vue affiche et retourne la vue suivante.
- `vue_abstraite.py` → classe de base **VueAbstraite**
- `session.py` → **Session** (utilisateur + session courante)
- `accueil_vue.py` → **AccueilVue** (menu principal : connexion, inscription, reset)
- `connexion_vue.py` → **ConnexionVue** (authentification)
- `inscription_vue.py` → **InscriptionVue** (création compte)
- `menu_utilisateur_vue.py` → **MenuUtilisateurVue** (après connexion)
- `reponseIA_vue.py` → **ReponseIAVue** (chat avec ensai-GPT)
- `historique_vue.py` → **HistoriqueVue** (liste conversations passées)
- `parametres_vue.py` → **ParametresVue** (modifier préférences)
- `personnages_vue.py` → **PersonnagesVue** (choisir/créer un persona IA)
- `stats_vue.py` → **StatsVue** (statistiques)

### `src/utils`
Outils techniques et fonctions transverses.
- `log_init.py` → initialisation des logs (via `logging_config.yml`)
- `log_decorator.py` → décorateur pour tracer les appels (entrée/sortie)
- `reset_database.py` → réinitialisation de la base (dev)
- `securite.py` → hashage et vérification des mots de passe
- `singleton.py` → pattern **Singleton** (connexion DB)
- `ia_client.py` → **IAClient** : appels API `POST /generate` (history, temperature, top_p, max_tokens)

### `src` (fichiers racine)
Point d’entrée de l’application et webservice.
- `main.py` → lance l’application **CLI** (enchaîne les vues)
- `app.py` → webservice **FastAPI** (routes REST : utilisateurs, sessions, messages, stats)

---

## Dossier `tests`
Tests unitaires avec **pytest**.
- `test_dao/test_utilisateur_dao.py`
- `test_dao/test_personnage_dao.py`
- `test_dao/test_chat_dao.py`
- `test_dao/test_settings_dao.py`
- `test_service/test_auth_service.py`
- `test_service/test_chat_service.py`
- `test_service/test_stats_service.py`
- `conftest.py` → fixtures (connexion test, nettoyage schéma)

---

## Dossier `doc`
Documentation et rendus.
- `doc/suivi/` → notes et rendus hebdomadaires du projet
- `doc/logs/` → fichiers de logs générés automatiquement
- `doc/diagrammes/` → diagrammes UML/sequence (Mermaid/PlantUML)
- `README_DOC.md` → doc détaillée (installation, décisions, etc.)

---

## Fichiers racine
- `.env` → variables d’environnement (PostgreSQL + API IA)
- `requirements.txt` → dépendances Python
- `logging_config.yml` → configuration YAML pour les logs
- `.coveragerc` → configuration coverage
- `.github/workflows/ci.yml` → pipeline CI (tests, lint, build auto)
- `LICENSE` → licence
- `README.md` → présentation du projet (features, installation, run)

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


