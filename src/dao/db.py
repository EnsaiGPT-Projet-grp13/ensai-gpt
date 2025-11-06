import os
import sys
import psycopg2
from psycopg2 import extras
from psycopg2.extras import RealDictCursor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv, find_dotenv
from src.utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """
    Connexion PostgreSQL unique (Singleton), robuste au répertoire courant.
    """

    def __init__(self):
        env_path = find_dotenv(filename=".env", usecwd=True)
        if not env_path:
            here = os.path.dirname(os.path.abspath(__file__))
            env_path = os.path.abspath(os.path.join(here, "..", "..", ".env"))
        load_dotenv(env_path, override=True)

        host = os.environ.get("POSTGRES_HOST", "").strip()
        port = int(os.environ.get("POSTGRES_PORT", "5432").strip())
        db   = os.environ.get("POSTGRES_DATABASE", "").strip()
        user = os.environ.get("POSTGRES_USER", "").strip()
        pwd  = os.environ.get("POSTGRES_PASSWORD", "").strip()
        schema = os.environ.get("POSTGRES_SCHEMA", "projetGPT").strip()

        self.__connection = psycopg2.connect(
            host=host,
            port=port,
            database=db,
            user=user,
            password=pwd,
            options=f"-c search_path={schema}",
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        return self.__connection
