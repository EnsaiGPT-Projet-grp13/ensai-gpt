import logging
from abc import ABC


class VueAbstraite(ABC):
    """Modèle de Vue"""

    def __init__(self, message: str = ""):
        self.message = message
        logging.info(type(self).__name__)

    def nettoyer_console(self):
        for _ in range(30):
            print("")

    def afficher(self) -> None:
        self.nettoyer_console()
        msg = getattr(self, "message", "")
        if msg:
            print(msg)
            print()
