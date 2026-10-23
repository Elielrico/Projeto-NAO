# -*- coding: utf-8 -*-
from flask import Flask, jsonify, Response, request
from naoqi import ALProxy
import threading
import requests
import time

app = Flask(__name__)

IP = "169.254.65.171"
PORT = 9559

#Inicializando serviçõs do NAO
memory = ALProxy("ALMemory", IP, PORT)
motion = ALProxy("ALMotion", IP, PORT)
tts = ALProxy("ALTextToSpeech", IP, PORT)
asr = ALProxy("ALSpeechRecognition", IP, PORT)
#asr.unsubscribe("MeuReconhecedor")
tts.setVolume(0.6)

vocabulario = [
    "oi",
    "ola",
    "dançar",
    "parar",
    "beijos",
    "sair",
    "sim",
    "não"
]

def preparar_asr():
    print("Verificando estado do ASR...")
    try:
        asr.unsubscribe("MeuReconhecedor")
        print("ASR estava ativo. Foi desativado.")

    except Exception as e:
        print("ASR já estava desativado.")

    asr.setVocabulary(vocabulario, False)

    asr.subscribe("MeuReconhecedor")

    print("ASR preparado e ativado.")

def iniciar_servico():
    print("NAO está ouvindo...")

    try:
        while True:

            resultado = memory.getData("WordRecognized")

            if resultado:
                print("Reconhecido:", resultado)
                s = resultado[0]

                if s.lower() in ['sair', 'exit', 'quit']:
                    print("Robô NAO: Tchau! Até a próxima.")
                    asr.unsubscribe("MeuReconhecedor")
                    break
                rota = "http://127.0.0.1:5001/modo_ia"
                try:
                    requests.post(rota,json={"palavra": s} ,timeout=30.0)
                except Exception as e:
                    print("Erro ao chmar rota!!!!! {}\n".format(e))
            
            memory.insertData("WordRecognized", "") #limpa a memoria

        time.sleep(0.1)

    except KeyboardInterrupt:
        asr.unsubscribe("MeuReconhecedor")

@app.route('/falar', methods=['POST'])
def falar():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "erro",
                "mensagem": "JSON não recebido"
            }), 400

        resposta_nao = data.get("resposta", "")

        print("\nEle entrou pra falar")
        print("Resposta:", resposta_nao)

        if resposta_nao == "":
            return jsonify({
                "status": "erro",
                "mensagem": "Resposta vazia"
            }), 400

        if resposta_nao == "vazio":
            tts.say("Nao consigo ler nada")

        else:
            # Converte Unicode para UTF-8
            if isinstance(resposta_nao, unicode):
                resposta_nao = resposta_nao.encode('utf-8')

            tts.say(resposta_nao)

        return jsonify({
            "status": "ok",
            "resposta": "fala executada"
        })

    except Exception as e:
        print("Erro de execução de fala: {}".format(e))

        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

if __name__ == '__main__':
    preparar_asr()
    # Inicia a thread de confirmação de inicialização (START)
    thread = threading.Thread(target=iniciar_servico)
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)