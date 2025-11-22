# **Projet Informatique 2A ENSAI – EnsaiGPT (Grp13)**

## **Description**
Ce projet est réalisé dans le cadre du **Projet Informatique de 2ème année à l’ENSAI**.  
Il met en œuvre une architecture en couches (DAO, service, view, business_object), une base de données PostgreSQL, une interface en ligne de commande avec InquirerPy, et un webservice construit avec FastAPI.  
Un module de **Chat IA** est intégré grâce à l’API :  
👉 [API ENSAI-GPT](https://ensai-gpt-109912438483.europe-west4.run.app/docs#/default/chat_generate_post)


## **Lancer l'application**

### **1- Initialiser l'environnement.**

Sur Oxyxia (ou SSPCloud) : lancer VScode, lancer PostGreSQL, lancer CloudBeaver

### **1- Cloner le projet dans Datalab (VSCode-python).**

```python
git clone https://github.com/EnsaiGPT-Projet-grp13/ensai-gpt
````

### **2- Créer et activer un environnement virtuel avec les dépendances**

Dans la racine du projet :

```python
cd ensai-gpt/
python -m venv .venv
source ~/work/ensai-gpt/.venv/bin/activate
pip install -r requirements.txt
````

### **3- Configurer la base de données**

 Dans la racine, créer un fichier .env et copier les lignes suivantes :

```python
WEBSERVICE_HOST=https://ensai-gpt-109912438483.europe-west4.run.app
LLM_TEMPERATURE=0.7
LLM_TOP_P=1.0
LLM_MAX_TOKENS=200

POSTGRES_HOST=           # ⚠️ à remplacer par votre host
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=           # ⚠️ à remplacer par votre identifiant
POSTGRES_PASSWORD=       # ⚠️ à remplacer par votre mot de passe
POSTGRES_SCHEMA=projetGPT
````

Pour initialiser et remplir la base de données, lancer :

```python
python data/setup_db.py
````
Si tout est correct tu devrais voir,  "Base/Schéma initialisés dans `projetGPT`"


### **4- Lancer l’application**

Démarre l’interface en ligne de commande :

```python
python src/main.py
````

## **Tests unitaires**

Exécuter :  

```python
pytest -v
````

### Couverture des tests
Il est possible de générer un rapport de couverture avec :  

```python
coverage run -m pytest
coverage report -m
coverage html
````

-> Ouvrir `coverage_report/index.html` pour un rapport détaillé.  

## **Structure du Projet**

### Dossier `data`
Scripts SQL et initialisation de la base de données.

### Dossier `src`
Code source principal : objets métiers, DAO, services, vues CLI et API.

### Dossier `tests`
Tests unitaires et d’intégration (pytest).

### Dossier `doc`
Documentation technique, schémas et suivi du projet.

---

# **Computer Science Project – 2nd Year ENSAI – EnsaiGPT (Group 13)**

## **Description**
This project was carried out as part of the **2nd-year Computer Science Project at ENSAI**.  
It implements a layered architecture (DAO, service, view, business_object), a PostgreSQL database, a command-line interface using InquirerPy, and a web service built with FastAPI.  
An **AI Chat** module is integrated through the API:  
👉 https://ensai-gpt-109912438483.europe-west4.run.app/docs#/default/chat_generate_post

## **Launching the Application**

### **1 – Initialize the environment.**

On Oxyxia (or SSPCloud): launch VSCode, start PostgreSQL, launch CloudBeaver.

### **1 – Clone the project in Datalab (VSCode-Python).**

```
git clone https://github.com/EnsaiGPT-Projet-grp13/ensai-gpt
```

### **2 – Create and activate a virtual environment with the dependencies**

In the project root:

```
cd ensai-gpt/
python -m venv .venv
source ~/work/ensai-gpt/.venv/bin/activate
pip install -r requirements.txt
```

### **3 – Configure the database**

In the root directory, create a `.env` file and copy the following lines:

```
WEBSERVICE_HOST=https://ensai-gpt-109912438483.europe-west4.run.app
LLM_TEMPERATURE=0.7
LLM_TOP_P=1.0
LLM_MAX_TOKENS=200

POSTGRES_HOST=           # ⚠️ replace with your host
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=           # ⚠️ replace with your username
POSTGRES_PASSWORD=       # ⚠️ replace with your password
POSTGRES_SCHEMA=projetGPT
```

To initialize and populate the database, run:

```
python data/setup_db.py
```

If everything is correct, you should see:  
**"Database/Schema initialized in `projetGPT`"**

### **4 – Launch the application**

Start the command-line interface:

```
python src/main.py
```

## **Unit Tests**

Run:

```
pytest -v
```

### Test coverage

Generate a coverage report with:

```
coverage run -m pytest
coverage report -m
coverage html
```

→ Open `coverage_report/index.html` for a detailed report.

## **Project Structure**

### `data` folder  
SQL scripts and database initialization.

### `src` folder  
Main source code: business objects, DAO, services, CLI and API views.

### `tests` folder  
Unit and integration tests (pytest).

### `doc` folder  
Technical documentation, diagrams, and project tracking.


