import subprocess
import sys

# init_db.py
subprocess.run([sys.executable, "data/init_db.py"], check=True)

# pop_db.py
subprocess.run([sys.executable, "data/pop_db.py"], check=True)

print("Base de données initialisée avec succès.")
