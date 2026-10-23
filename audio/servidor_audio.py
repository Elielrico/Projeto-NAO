
# servidor_audio.py
from flask import Flask, send_from_directory
import os

app = Flask(__name__)

AUDIOS = {
    "audio1": "obrigado-amigo-voce-e-um-amigo.mp3",
    "audio2": "notificacao.mp3", 
    "audio3": "aham-sei.mp3",
    "audio4": "risada-minions.mp3",
    "audio5": "risadas-com-aplausos.mp3"
}

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = "obrigado-amigo-voce-e-um-amigo.mp3"

@app.route("/audio")
def audio():
    caminho = os.path.join(PASTA, AUDIOS["audio5"])

    if not os.path.isfile(caminho):
        return "MP3 nao encontrado: " + caminho, 404

    return send_from_directory(
        PASTA,
        AUDIOS["audio5"],
        mimetype="audio/mpeg"
    )

app.run(host="0.0.0.0", port=8000, debug=False)
