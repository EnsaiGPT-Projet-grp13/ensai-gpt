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


.
├── data/                               # Scripts et données pour la BDD
│   ├── init_db.py                      # Création du schéma et tables
│   ├── pop_db.py                       # Jeu de données exemple
│   └── sql/                            # (Optionnel) Scripts SQL
│       ├── schema.sql
│       └── seed.sql
│
├── doc/                                # Documentation du projet
│   ├── suivi/                          # Notes d’avancement hebdo
│   ├── logs/                           # Logs générés automatiquement
│   ├── diagrammes/                     # Diagrammes UML, schémas
│   └── README_DOC.md
│
├── ensai-gpt/                          # Dossier principal de l’application
│   ├── __init__.py
│
│   ├── business_object/                # Objets métiers (simples POJO)
│   │   ├── utilisateur.py              # Classe Utilisateur
│   │   ├── personnage_ia.py            # Classe PersonnageIA (prof, cuisinier, jardinier…)
│   │   ├── chat.py                     # ChatSession, ChatMessage
│   │   ├── settings.py                 # UserSettings (température, style…)
│   │   └── stats.py                    # Statistiques utilisateur
│
│   ├── dao/                            # Accès à la base (CRUD)
│   │   ├── db_connection.py            # Connexion PostgreSQL (singleton)
│   │   ├── utilisateur_dao.py          # CRUD utilisateurs
│   │   ├── personnage_dao.py           # CRUD personnages IA
│   │   ├── chat_session_dao.py         # CRUD sessions
│   │   ├── chat_message_dao.py         # CRUD messages
│   │   ├── settings_dao.py             # CRUD préférences
│   │   └── stats_dao.py                # Calculs/statistiques
│
│   ├── service/                        # Logique applicative
│   │   ├── auth_service.py             # Inscription / Connexion
│   │   ├── utilisateur_service.py      # Gestion du profil
│   │   ├── personnage_service.py       # Gestion des personnages IA
│   │   ├── chat_service.py             # Gestion des sessions de chat
│   │   ├── settings_service.py         # Gestion des préférences
│   │   ├── search_service.py           # Recherche historique
│   │   ├── stats_service.py            # Statistiques globales
│   │   └── export_service.py           # Export carnet de bord (PDF/CSV)
│
│   ├── view/                           # Interface CLI (InquirerPy)
│   │   ├── vue_abstraite.py            # Classe de base Vue
│   │   ├── session.py                  # Session (utilisateur courant)
│   │   ├── accueil_vue.py              # Accueil : connexion/inscription
│   │   ├── connexion_vue.py            # Connexion
│   │   ├── inscription_vue.py          # Inscription
│   │   ├── menu_utilisateur_vue.py     # Menu utilisateur (après login)
│   │   ├── reponseIA_vue.py            # Chat avec IA
│   │   ├── historique_vue.py           # Historique conversations
│   │   ├── parametres_vue.py           # Modification préférences
│   │   ├── personnages_vue.py          # Choix/Création personnages
│   │   └── stats_vue.py                # Vue statistiques utilisateur
│
│   ├── utils/                          # Outils techniques
│   │   ├── log_init.py                 # Initialisation logs
│   │   ├── log_decorator.py            # Décorateurs de logs
│   │   ├── reset_database.py           # Reset BDD
│   │   ├── securite.py                 # Hashage/vérification mots de passe
│   │   ├── singleton.py                # Pattern Singleton
│   │   └── ia_client.py                # Client API ENSAI-GPT (/generate)
│
│   ├── main.py                         # Point d’entrée CLI
│   └── app.py                          # Webservice FastAPI
│
├── tests/                              # Tests unitaires (pytest)
│   ├── test_dao/
│   │   ├── test_utilisateur_dao.py
│   │   ├── test_personnage_dao.py
│   │   ├── test_chat_dao.py
│   │   └── test_settings_dao.py
│   ├── test_service/
│   │   ├── test_auth_service.py
│   │   ├── test_chat_service.py
│   │   └── test_stats_service.py
│   └── conftest.py
│
├── .github/workflows/ci.yml            # CI/CD (tests, lint, build)
├── .coveragerc                         # Config coverage
├── .gitignore
├── LICENSE
├── README.md                           # Présentation projet
├── requirements.txt                    # Dépendances Python
├── logging_config.yml                  # Config logs
└── .env                                # Variables d’environnement

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


