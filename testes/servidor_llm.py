from flask import Flask, jsonify, request
import requests
import ollama

app = Flask(__name__)

url = "http://127.0.0.1:5000/falar"

mensagens = [
        {'role': 'system','content': 'Você é o robô NAO. Responda com frases curtas e tom acolhedor.'},
        {'role': 'system','content': 'Você tem que fazer perguntas apenas pra as pessoas responderem sim ou não'}
    ]

@app.route('/modo_ia', methods=['POST'])
def executar_llama():
    #return jsonify({"status": "iniciado"})
    data = request.json

    if not data or 'palavra' not in data:
        return jsonify({
            "status": "erro",
            "mensagem": "Campo 'palavra' não foi enviado."
        }), 400

    entrada_usuario = data['palavra']

    print("Entrada: {}\n".format(entrada_usuario))

    if entrada_usuario != "":
        print("Recebeeeeeeeuuuuu")
        # Adiciona a mensagem do usuário ao histórico
        mensagens.append({'role': 'user', 'content': entrada_usuario})
        try:
            # Envia todo o histórico atualizado para o Ollama
            response = ollama.chat(
                model='robo_nao',  # Ou 'llama3.2'
                messages=mensagens
            )
                    
            # Extrai a resposta da IA
            resposta_robo = response['message']['content']
                    
            # Exibe a resposta na tela
            print(f"Robô NAO: {resposta_robo}\n")
                    
            # Salva a resposta do robô no histórico para dar sequência à conversa
            mensagens.append({'role': 'assistant', 'content': resposta_robo})

            try:
                requests.post(url,json={"resposta": resposta_robo} ,timeout=2.0)
            except Exception as e:
                print("Erro ao chamar rota!!!!! {}\n".format(e))

            #return jsonify({"resposta": resposta_robo})
        
        except Exception as e:
            print(f"Erro ao se comunicar com o Ollama: {e}\n")
        return jsonify({
            "status": "ok",
            "resposta": resposta_robo
        })
    else:
        print("Nãoooooooooooooo recebeu")
        try:
            requests.post(url,json={"resposta": "vazio"} ,timeout=2.0)
        except Exception as e:
            print("Erro ao chamar rota!!!!! {}\n".format(e))
        return jsonify({
            "status": "ok",
            "resposta": "vazio"
        })
    

if __name__ == '__main__':
    # Executa a lógica antes de iniciar o servidor

    app.run(host='0.0.0.0', port=5001, debug=False)