# -*- coding: utf-8 -*-
import os
import importlib
import math
import almath as m
from flask import Flask, jsonify, render_template, request, Response
from naoqi import ALProxy
from movimentos.headMove import inicializar_e_rastrear
import vision_definitions
import requests
import base64
import threading
import time
import numpy as np

app = Flask(__name__)

ROBOT_IP = None
PORT = None
motion_proxy = None
posture_proxy = None
memory_proxy = None
status_cam = 0

@app.route('/conectar', methods=['POST'])
def conectar():
    global ROBOT_IP, PORT, motion_proxy, posture_proxy, memory_proxy
    
    data = request.json
    if not data:
        return jsonify({"status": "erro", "mensagem": "Dados JSON nao recebidos"}), 400

    ROBOT_IP = str(data.get('ip'))
    PORT = int(data.get('port'))

    inicializar_e_rastrear(ROBOT_IP, PORT)

    print("Tentando conectar ao NAO em: {}:{}".format(ROBOT_IP, PORT))

    try:
        print("Conectando ao NAO...")
        motion_proxy = ALProxy("ALMotion", ROBOT_IP, PORT)
        posture_proxy = ALProxy("ALRobotPosture", ROBOT_IP, PORT)
        memory_proxy = ALProxy("ALMemory", ROBOT_IP, PORT)
        return jsonify({
            "status": "sucesso", 
            "mensagem": "Conectado com sucesso ao NAO!"
        })
    except Exception as e:
        print("Erro na conexao: {}".format(str(e)))
        # IMPORTANTE: Você tambem precisa retornar algo aqui em caso de erro!
        return jsonify({
            "status": "erro", 
            "mensagem": "Falha ao conectar: " + str(e)
        }), 500  

# Dicionário global que armazenará as funções de movimento
ACOES = {}
PASTA_MOVIMENTOS = "movimentos"

#####################
## get robot position before move
#####################
initRobotPosition = None

def carregar_movimentos():
    """ Escaneia a pasta 'movimentos' e importa todas as funções automaticamente """
    print("\n--- Carregando Movimentos ---")
    
    # Garante que a pasta existe
    if not os.path.exists(PASTA_MOVIMENTOS):
        os.makedirs(PASTA_MOVIMENTOS)
        return

    for arquivo in os.listdir(PASTA_MOVIMENTOS):
        if arquivo.endswith(".py") and arquivo != "__init__.py":
            nome_modulo = arquivo[:-3]  # Remove o '.py'
            
            try:
                modulo = importlib.import_module(PASTA_MOVIMENTOS + "." + nome_modulo)
                
                for nome_funcao in dir(modulo):
                    funcao = getattr(modulo, nome_funcao)
                    
                    # Verifica se é uma função e se o nome bate (independente de maiúsculas)
                    if callable(funcao) and nome_funcao.lower() == nome_modulo.lower():
                        # SALVAMOS SEMPRE EM MINÚSCULO PARA NÃO TER ERRO NA URL
                        chave_da_url = nome_modulo.lower() 
                        ACOES[chave_da_url] = funcao
                        print("Sucesso: Comando pronto em -> /executar/{}".format(chave_da_url))
            except Exception as e:
                print("Erro ao carregar modulo {}: {}".format(nome_modulo, e))
    print("-----------------------------\n")

# --- ROTAS FLASK ---
@app.route('/')
def home():
    global ROBOT_IP, PORT
    """ Página principal para o celular """
    # Passamos a lista de ações para o HTML gerar os botões sozinho
    return render_template('index.html', acoes=ACOES.keys(), robot_ip=ROBOT_IP, port=PORT)

@app.route('/<nome_reacao>')
def api_reacao(nome_reacao):
    """ Rota que o celular chama ao clicar no botão """
    if nome_reacao not in ACOES:
        return jsonify({"status": "erro", "mensagem": "Reacao nao encontrada"}), 404

    try:
        # 1. Busca os dados do arquivo .py (names, times, keys, label)
        names, times, keys, label = ACOES[nome_reacao]()
        
        if motion_proxy:
            # 2. Ativa os motores (Stiffness)
            motion_proxy.stiffnessInterpolation("Body", 1.0, 1.0)

            # 3. Executa a interpolação
            # Ordem do NAOqi: nomes, chaves (ângulos), tempos
            motion_proxy.angleInterpolation(names, keys, times, True)

            return jsonify({"status": "sucesso", "acao": label})

    except Exception as e:
        print("Erro no Robo: " + str(e))
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/move', methods=['POST'])
def move():
    global initRobotPosition 
    data = request.json
    if not data:
        return jsonify({"status": "erro", "mensagem": "Dados JSON nao recebidos"}), 400
    x_atual = float(data.get('x', 0))
    y_atual = float(data.get('y', 0))
    theta_atual = float(data.get('theta', 0))
    y_angle = float(data.get('y_rot', 0))

    print("x: {}\ny: {}\ntheta: {}\n".format(x_atual, y_atual, theta_atual))

    try:

        if motion_proxy:
            if x_atual == 0 and y_atual == 0 and theta_atual == 0:
                motion_proxy.stopMove()
                motion_proxy.moveInit()
                #posture_proxy.goToPosture("StandInit", 0.5)
                #####################
                ## get robot position after move
                #####################
                endRobotPosition = m.Pose2D(motion_proxy.getRobotPosition(False))

                #####################
                ## compute and print the robot motion
                #####################
                robotMove = m.pose2DInverse(initRobotPosition)*endRobotPosition
                # return an angle between ]-PI, PI]
                robotMove.theta = m.modulo2PI(robotMove.theta)
                roll = 0.0
                print ("Robot Move:", robotMove)
                return jsonify(status="success") 
    
            else:
                th = math.acos(y_angle)
                #mapeando o angulo do joiystick para os angulos do NAO
                if theta_atual > 0 and theta_atual < (math.pi)/2:
                    angle = -0.3
                    roll = memory_proxy.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value")
                    print("roll: {}\nth: {}\n".format(roll, th))
                    if roll == th:
                        angle = 0.0
                elif theta_atual > (math.pi)/2  and theta_atual < (math.pi):
                    angle = 0.3
                    roll = memory_proxy.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value")
                    print("roll: {}\nth: {}\n".format(roll, th))
                    if roll == th:
                        angle = 0.0
                elif theta_atual > (math.pi) and theta_atual < (3*(math.pi))/2:
                    angle = 0.3
                    roll = memory_proxy.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value")
                    print("roll: {}\nth: {}\n".format(roll, th))
                    if roll == th:
                        angle = 0.0
                elif theta_atual > (3*(math.pi))/2 and theta_atual < (math.pi)*2:
                    angle = -0.3
                    roll = memory_proxy.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value")
                    print("roll: {}\nth: {}\n".format(roll, th))
                    if roll == th:
                        angle = 0.0
                else:
                    angle = 0.0
                print("Angle: {}\n".format(angle))
                # Se o movimento está começando agora e a posição inicial é nula, capturamos ela
                if 'initRobotPosition' not in globals() or initRobotPosition is None:
                    initRobotPosition = m.Pose2D(motion_proxy.getRobotPosition(False))
                    #####################
                ## Habilitar o controle dos braços por meio do algoritmo de movimento
                #####################
                motion_proxy.setMoveArmsEnabled(True, True)
                #~ motionProxy.setMoveArmsEnabled(False, False)
                #####################
                ## FOOT CONTACT PROTECTION
                #####################
                #motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", False]])
                motion_proxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])
                try:
                    motion_proxy.moveToward(x_atual, y_atual, angle,
                    [ ["MaxStepX", 0.02],       # step of 4 cm in front
                    ["MaxStepY", 0.16],         # default value
                    ["MaxStepTheta", 0.4],      # default value
                    ["MaxStepFrequency", 0.0],  # low frequency
                    ["StepHeight", 0.01],       # step height of 1 cm
                    ["TorsoWx", 0.0],           # default value
                    ["TorsoWy", 0.1] ])         # torso bend 0.1 rad in front
                    return jsonify(status="success")        
                except Exception as e:
                    print("Erro de execucao: {}".format(str(e)))
                    return jsonify({
                    "status": "erro", 
                    "mensagem": "Falha ao executar movimento: " + str(e)
                    }), 500 
                      
    except Exception as e:
        print("Erro de execucao: {}".format(str(e)))
        # IMPORTANTE: Você tambem precisa retornar algo aqui em caso de erro!
        return jsonify({
            "status": "erro", 
            "mensagem": "Falha ao executar movimento: " + str(e)
        }), 500 

@app.route('/joystick_page')
def abrir_joystick():
    return render_template('joystick.html')

@app.route('/camera', methods=['POST'])
def start_camera():
    global status_cam
    data = request.json
    status_cam = float(data.get('status_camera', 0))

    if status_cam:
        # 2. Criamos o ajudante (Thread) para rodar o loop sem travar o Flask
        threading.Thread(target=stream_nao_frames).start()
        return jsonify(status="Camera ligada")
    
    else:
        return jsonify(status="Camera parando...")

def stream_nao_frames():
    videoProxy = ALProxy("ALVideoDevice", ROBOT_IP, PORT)
    resolution = vision_definitions.kQVGA # 320x240
    colorSpace = vision_definitions.kRGBColorSpace
    
    client = videoProxy.subscribe("python_client", resolution, colorSpace, 5)
    
    try:
        while status_cam == 1:
            naoImage = videoProxy.getImageRemote(client)
            if naoImage is None:
                continue

            width = naoImage[0]
            height = naoImage[1]
            image_data = naoImage[6]

            url = "http://127.0.0.1:5001/frame"

            # Codificar imagem em base64
            img_base64 = base64.b64encode(image_data).decode('utf-8')

            # Enviar para o servidor Flask --> Python 3
            try:
                requests.post(url,
                    json={
                        "width": width,
                        "height": height,
                        "image": img_base64,
                        "status": status_cam
                    },
                    timeout=2.0 # Timeout curto para não acumular atraso
                )
                
            except Exception as e:
                print("Erro ao postar frame: {}".format(e))
            #pausa para enciar aproximadamente 14 frames por segundo
            time.sleep(0.07)
                
    finally:
        videoProxy.unsubscribe(client)
        print("Câmera desligada")

@app.route('/falar_page')
def abrir_fala():
    return render_template('speek.html')

@app.route('/reconhecer_page')
def abrir_reconhecimento():
    return render_template('rec_facial.html')

@app.route('/falar', methods=['POST'])
def falarTexto():
    global motion_proxy, ROBOT_IP, PORT
    try:
        data = request.json
        txt = str(data.get('texto'))

        motion_proxy.moveInit()
        tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
        tts.setParameter("speed", 75)
        tts.setParameter("pitchShift", 1.1)
        tts.say(txt)
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        #return "Falha ao executar comando de fala! " + str(e), 500
        return jsonify({"status": "erro"}), 500

@app.route('/movehead', methods=['POST'])
def moveHead():
    data = request.json
    if not data:
        return jsonify({"status": "erro", "mensagem": "JSON ausente"}), 400

    y_head = float(data.get('yh', 0))
    x_head = float(data.get('xh', 0))

    # Mapeamento e conversão EXPLÍCITA para float nativo do Python
    angulo_yaw = float(np.interp(x_head, [-1, 1], [-2.08, 2.08]))
    angulo_pitch = float(np.interp(y_head, [-1, 1], [-0.67, 0.51]))

    print("Angulo Yaw: {}, Pitch: {}".format(angulo_yaw, angulo_pitch))

    try:
        global motion_proxy
        
        # Ativa a rigidez apenas na cabeça (valores de 0.0 a 1.0)
        motion_proxy.setStiffnesses("Head", 1.0)
        
        # Envia os ângulos convertidos
        motion_proxy.setAngles(["HeadYaw", "HeadPitch"], [angulo_yaw, angulo_pitch], 0.2)
        
        return jsonify({"status": "sucesso", "yaw": angulo_yaw, "pitch": angulo_pitch}), 200

    except Exception as e:
        # Imprime o erro exato do SDK NAOqi no terminal
        print("Erro ao mover a cabeça do NAO:", str(e))
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/emergencia')
def parada_emergencia():
    global motion_proxy
    try:
        motion_proxy.stopMove()
        motion_proxy.post.rest()
        return "Protocolo de emergencia executado!", 200
    except Exception as e:
        return "Falha ao executar comando: " + str(e), 500

@app.route('/pose_seguranca', methods=['POST'])
def poseSeguranca():
    global motion_proxy
    data = request.json
    posicao = int(data.get('pose', 0))

    try:
        if posicao == 1:
            motion_proxy.rest()
        else:
            motion_proxy.wakeUp()
            motion_proxy.moveInit()
        return "Protocolo de posição de segurança executado!", 200
    except Exception as e:
        return "Falha ao executar comando: " + str(e), 500


# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    # 1. Carrega os arquivos da pasta
    carregar_movimentos()
    # host='0.0.0.0' permite conexão externa (celular)
    app.run(host='0.0.0.0', port=5000, debug=False)