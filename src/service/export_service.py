from flask import Flask, Response, request
import threading
import socket
import io
from dao.message_dao import MessageDao

app = Flask(__name__)


class ExportService:
    """Gestion du téléchargement/export"""

    def __init__(self):
        self.message_dao = MessageDao()

    def generer_message_conversation(self, id_conversation: int, titre: str = "Conversation"):
        """Renvoie le contenu texte de la conversation sans sauvegarder de fichier"""
        liste_message = self.message_dao.list_for_conversation(id_conversation)
        if not liste_message:
            return None

        contenu = "\n" + "-" * 50 + f"\n Conversation : {titre}\n" + "-" * 50 + "\n"
        for message in liste_message:
            contenu += f"\nMessage de {message.expediteur} : " + "-" * 50 + "\n" + f"{message.contenu}\n\n"
        return contenu


export_service = ExportService()


@app.route("/telecharger/<int:id_conversation>")
def telecharger(id_conversation: int):
    """Renvoie la conversation sous forme de fichier téléchargeable"""
    try:
        titre_fichier = request.args.get("titre", "Conversation")
        nom_fichier = request.args.get("fichier", "conversation.txt")

        print(f"Téléchargement demandé : id={id_conversation}, titre={titre_fichier}, fichier={nom_fichier}")

        contenu = export_service.generer_message_conversation(id_conversation, titre_fichier)
        if not contenu:
            return "Aucun message trouvé pour cette conversation.", 404

        buffer = io.BytesIO(contenu.encode("utf-8"))

        headers = {
            "Content-Disposition": f"attachment; filename={nom_fichier}"
        }

        return Response(buffer, mimetype="text/plain", headers=headers)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Erreur interne : {e}", 500


def start_flask_server():
    """Démarre le serveur Flask en tâche de fond s'il n'est pas déjà lancé."""
    import time

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", 5000))
    sock.close()
    if result == 0:
        print("Serveur Flask déjà en cours sur http://127.0.0.1:5000")
        return

    def run():
        app.run(host="127.0.0.1", port=5000, debug=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    time.sleep(1)
    print("🌐 Serveur Flask lancé sur http://127.0.0.1:5000")
