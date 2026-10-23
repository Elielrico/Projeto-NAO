# -*- coding: utf-8 -*-
from naoqi import ALProxy
import time
from beijos import Beijos
#import ollama

IP = "169.254.65.171"
PORT = 9559
# ---------- Conectando aos serviços do NAO ----------
memory = ALProxy("ALMemory", IP, PORT)

motion = ALProxy("ALMotion", IP, PORT)
#motion.setStiffnesses("Body", 1.0)

life = ALProxy("ALAutonomousLife", IP, PORT)
print("Autonomous Life:", life.getState())
#life.setState("disabled")

awareness = ALProxy("ALBasicAwareness", IP, PORT)
awareness.stopAwareness()

asr = ALProxy("ALSpeechRecognition", IP, PORT)
#asr.unsubscribe("MeuReconhecedor")
#asr.setLanguage("Portuguese")

#---------- Criando prompt para LLM (historico) ----------
mensagens = [
        {'role': 'system','content': 'Você é o robô NAO. Responda com frases curtas e tom acolhedor.'},
        {'role': 'system','content': 'Você tem que fazer perguntas apenas pra as pessoas responderem sim ou não'}
    ]

vocabulario = [
    "oi",
    "ola",
    "dançar",
    "parar",
    "beijos",
    "sair"
]

asr.setVocabulary(vocabulario, False)

asr.subscribe("MeuReconhecedor")

print("NAO está ouvindo...")

try:
    while True:

        resultado = memory.getData("WordRecognized")

        if resultado:
            print("Reconhecido:", resultado)
            s = resultado[0]

            if s == "ola":
                print("QUÉ BARATAAAA")
            if s == "beijos":
                print("Começando os movimentos")
                motion.wakeUp()
                #motion.setStiffnesses("Body", 1.0)
                print("Autonomous Life:", life.getState())
                names, times, keys, nome = Beijos()
                print("Tá indo")
                motion.angleInterpolation(names, keys, times, True)
                print("ALOHAAAAAA")
                s = ""
                memory.insertData("WordRecognized", "") #limpa a memoria
                print("continua")
                motion.rest()

            if s.lower() in ['sair', 'exit', 'quit']:
                print("Robô NAO: Tchau! Até a próxima.")
                asr.unsubscribe("MeuReconhecedor")
                motion.rest()
                break
                        
            """# Ignora envios vazios (se o usuário só pressionar Enter)
            if not s.strip():
                continue
                
            # Adiciona a mensagem do usuário ao histórico
            mensagens.append({'role': 'user', 'content': s})
                
            try:
                # Envia todo o histórico atualizado para o Ollama
                response = ollama.chat(
                    model='teste_ia',  # Ou 'llama3.2'
                    messages=mensagens
                )
                            
                # Extrai a resposta da IA
                resposta_robo = response['message']['content']
                            
                # Exibe a resposta na tela
                #print(f"Robô NAO: {resposta_robo}\n")
                print("Resposta do NAO: {}\n".format(resposta_robo))
                            
                #Salva a resposta do robô no histórico para dar sequência à conversa
                mensagens.append({'role': 'assistant', 'content': resposta_robo})
                
            except Exception as e:
                #print(f"Erro ao se comunicar com o Ollama: {e}\n")
                print("Erro ao se comunicar com o Ollama: {}\n".format({e})) """

        time.sleep(0.1)

except KeyboardInterrupt:
    asr.unsubscribe("MeuReconhecedor")