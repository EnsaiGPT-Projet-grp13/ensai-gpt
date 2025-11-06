import subprocess
import sys

# Exécute init_db.py
subprocess.run([sys.executable, "init_db.py"], check=True)

# Exécute pop_db.py
subprocess.run([sys.executable, "pop_db.py"], check=True)

print("Base de données initialisée avec succès.")
