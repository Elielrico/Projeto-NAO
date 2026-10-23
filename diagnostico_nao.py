# -*- coding: utf-8 -*-

from naoqi import ALProxy
import time
import csv
import os
import sys
from datetime import datetime


# ============================================================
# CONFIGURAÇÃO
# ============================================================

ROBOT_IP = "169.254.179.49" 
PORT = 9559

INTERVALO = 0.5              # segundos entre medições

ARQUIVO_CSV = "diagnostico_nao.csv"


# ============================================================
# JUNTAS DO NAO
# ============================================================

JOINTS = [
    # Cabeça
    "HeadYaw",
    "HeadPitch",

    # Braço esquerdo
    "LShoulderPitch",
    "LShoulderRoll",
    "LElbowYaw",
    "LElbowRoll",
    "LWristYaw",

    # Braço direito
    "RShoulderPitch",
    "RShoulderRoll",
    "RElbowYaw",
    "RElbowRoll",
    "RWristYaw",

    # Perna esquerda
    "LHipYawPitch",
    "LHipRoll",
    "LHipPitch",
    "LKneePitch",
    "LAnklePitch",
    "LAnkleRoll",

    # Perna direita
    "RHipYawPitch",
    "RHipRoll",
    "RHipPitch",
    "RKneePitch",
    "RAnklePitch",
    "RAnkleRoll"
]


# ============================================================
# PROXIES
# ============================================================

print("")
print("==============================================")
print("       DIAGNOSTICO INTERNO DO NAO")
print("==============================================")
print("")

print("Conectando ao NAO em {}:{}...".format(ROBOT_IP, PORT))

try:

    motion = ALProxy("ALMotion", ROBOT_IP, PORT)
    memory = ALProxy("ALMemory", ROBOT_IP, PORT)
    battery = ALProxy("ALBattery", ROBOT_IP, PORT)
    posture = ALProxy("ALRobotPosture", ROBOT_IP, PORT)

    posture.goToPosture("StandInit", 0.5)

    print("Conexao estabelecida!")
    print("")

except Exception as e:

    print("ERRO AO CONECTAR AO NAO:")
    print(e)
    sys.exit(1)

# ============================================================
# VERIFICAÇÃO DOS SENSORES
# ============================================================

print("Verificando sensores...")
print("")


# ============================================================
# FUNÇÃO SEGURA PARA LEITURA
# ============================================================

def ler_memory(chave):

    try:
        return memory.getData(chave)

    except Exception:
        return None


def valor_numerico(valor):

    try:
        return float(valor)

    except Exception:
        return None


# ============================================================
# CABEÇALHO DO CSV
# ============================================================

arquivo_existe = os.path.exists(ARQUIVO_CSV)

csv_file = open(
    ARQUIVO_CSV,
    "ab"
)

# Python 2
writer = csv.writer(csv_file)


# ============================================================
# ESCREVE CABEÇALHO
# ============================================================

if not arquivo_existe:

    cabecalho = [
        "timestamp",
        "battery_percent",
        "battery_voltage",
        "posture",

        # IMU
        "acc_x",
        "acc_y",
        "acc_z",
        "gyro_x",
        "gyro_y",
        "gyro_z",
        "angle_x",
        "angle_y",

        # Pés
        "left_foot_contact",
        "right_foot_contact"
    ]

    # Dados de cada junta
    for joint in JOINTS:

        cabecalho.append(joint + "_temp")
        cabecalho.append(joint + "_current")
        cabecalho.append(joint + "_position_sensor")
        cabecalho.append(joint + "_position_command")
        cabecalho.append(joint + "_stiffness")

    writer.writerow(cabecalho)
    csv_file.flush()


# ============================================================
# FUNÇÃO PARA OBTER INFORMAÇÕES DA BATERIA
# ============================================================

def ler_bateria():

    porcentagem = None
    tensao = None

    try:
        porcentagem = battery.getBatteryCharge()

    except Exception:
        pass

    try:
        tensao = battery.getBatteryCharge()

    except Exception:
        pass

    # Tenta diretamente pelo ALMemory também
    try:
        tensao_mem = memory.getData(
            "Device/SubDeviceList/Battery/Charge/Sensor/Value"
        )

        if tensao_mem is not None:
            porcentagem = float(tensao_mem) * 100.0

    except Exception:
        pass

    try:
        tensao_mem = memory.getData(
            "Device/SubDeviceList/Battery/Current/Sensor/Value"
        )

        # Apenas mantém compatibilidade caso exista
        if tensao is None:
            tensao = tensao_mem

    except Exception:
        pass

    return porcentagem, tensao


# ============================================================
# FUNÇÃO PARA LER UMA JUNTA
# ============================================================

def ler_junta(joint):

    resultado = {
        "temperature": None,
        "current": None,
        "position_sensor": None,
        "position_command": None,
        "stiffness": None
    }

    # --------------------------------------------------------
    # Temperatura
    # --------------------------------------------------------

    chave = (
        "Device/SubDeviceList/{}/Temperature/Sensor/Value"
        .format(joint)
    )

    resultado["temperature"] = ler_memory(chave)


    # --------------------------------------------------------
    # Corrente
    # --------------------------------------------------------

    chave = (
        "Device/SubDeviceList/{}/ElectricCurrent/Sensor/Value"
        .format(joint)
    )

    resultado["current"] = ler_memory(chave)


    # --------------------------------------------------------
    # Encoder / posição medida
    # --------------------------------------------------------

    chave = (
        "Device/SubDeviceList/{}/Position/Sensor/Value"
        .format(joint)
    )

    resultado["position_sensor"] = ler_memory(chave)


    # --------------------------------------------------------
    # Posição comandada
    # --------------------------------------------------------

    chave = (
        "Device/SubDeviceList/{}/Position/Actuator/Value"
        .format(joint)
    )

    resultado["position_command"] = ler_memory(chave)


    # --------------------------------------------------------
    # Stiffness
    # --------------------------------------------------------

    try:

        resultado["stiffness"] = motion.getStiffnesses(
            [joint]
        )[0]

    except Exception:
        pass


    return resultado


# ============================================================
# FUNÇÃO PARA LER IMU
# ============================================================

def ler_imu():

    dados = {
        "acc_x": None,
        "acc_y": None,
        "acc_z": None,
        "gyro_x": None,
        "gyro_y": None,
        "gyro_z": None,
        "angle_x": None,
        "angle_y": None
    }

    # --------------------------------------------------------
    # Acelerômetro
    # --------------------------------------------------------

    dados["acc_x"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/Value"
    )

    dados["acc_y"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/Value"
    )

    dados["acc_z"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/Value"
    )


    # --------------------------------------------------------
    # Giroscópio
    # --------------------------------------------------------

    dados["gyro_x"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/GyrX/Sensor/Value"
    )

    dados["gyro_y"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/GyrY/Sensor/Value"
    )

    dados["gyro_z"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/GyrZ/Sensor/Value"
    )


    # --------------------------------------------------------
    # Ângulos da IMU
    # --------------------------------------------------------

    dados["angle_x"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value"
    )

    dados["angle_y"] = ler_memory(
        "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value"
    )


    return dados


# ============================================================
# SENSORES DOS PÉS
# ============================================================

def ler_pes():

    esquerdo = None
    direito = None

    try:

        esquerdo = memory.getData(
            "Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value"
        )

    except Exception:
        pass


    try:

        direito = memory.getData(
            "Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/Value"
        )

    except Exception:
        pass


    return esquerdo, direito


# ============================================================
# FUNÇÃO PARA MOSTRAR RESUMO
# ============================================================

def mostrar_resumo(
        timestamp,
        bateria,
        postura,
        imu,
        temperaturas,
        correntes):

    print("")
    print("============================================================")
    print("TEMPO:", timestamp)
    print("============================================================")

    print(
        "Bateria: {} %".format(
            bateria
        )
    )

    print(
        "Postura: {}".format(
            postura
        )
    )

    print("")
    print("IMU:")
    print(
        "  Acc: X={:.3f} Y={:.3f} Z={:.3f}".format(
            float(imu["acc_x"] or 0),
            float(imu["acc_y"] or 0),
            float(imu["acc_z"] or 0)
        )
    )

    print(
        "  Gyro: X={:.3f} Y={:.3f} Z={:.3f}".format(
            float(imu["gyro_x"] or 0),
            float(imu["gyro_y"] or 0),
            float(imu["gyro_z"] or 0)
        )
    )

    print(
        "  Angulo: X={:.3f} Y={:.3f}".format(
            float(imu["angle_x"] or 0),
            float(imu["angle_y"] or 0)
        )
    )

    print("")
    print("JUNTAS:")

    for joint in JOINTS:

        temp = temperaturas.get(joint)
        corrente = correntes.get(joint)

        if temp is not None or corrente is not None:

            print(
                "  {:18s} Temp={:6} C   Corrente={:8} A".format(
                    joint,
                    str(round(float(temp), 2)) if temp is not None else "N/A",
                    str(round(float(corrente), 3)) if corrente is not None else "N/A"
                )
            )


# ============================================================
# LOOP PRINCIPAL
# ============================================================

print("")
print("==============================================")
print("MONITORAMENTO INICIADO")
print("==============================================")
print("")
print("NAO DEVE SER COMANDADO PELO PROGRAMA.")
print("O programa apenas realiza leituras.")
print("")
print("Pressione CTRL+C para parar.")
print("")


try:

    while True:

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )


        # ====================================================
        # BATERIA
        # ====================================================

        bateria, tensao = ler_bateria()


        # ====================================================
        # POSTURA
        # ====================================================

        try:

            postura_atual = posture.getPostureFamily()

        except Exception:

            postura_atual = "ERRO"


        # ====================================================
        # IMU
        # ====================================================

        imu = ler_imu()


        # ====================================================
        # PÉS
        # ====================================================

        pe_esquerdo, pe_direito = ler_pes()


        # ====================================================
        # JUNTAS
        # ====================================================

        temperaturas = {}
        correntes = {}
        posicoes = {}
        comandos = {}
        stiffnesses = {}


        for joint in JOINTS:

            dados = ler_junta(joint)

            temperaturas[joint] = dados["temperature"]

            correntes[joint] = dados["current"]

            posicoes[joint] = dados["position_sensor"]

            comandos[joint] = dados["position_command"]

            stiffnesses[joint] = dados["stiffness"]


        # ====================================================
        # MOSTRA NO TERMINAL
        # ====================================================

        mostrar_resumo(
            timestamp,
            bateria,
            postura_atual,
            imu,
            temperaturas,
            correntes
        )


        # ====================================================
        # GRAVA CSV
        # ====================================================

        linha = [
            timestamp,
            bateria,
            tensao,
            postura_atual,

            imu["acc_x"],
            imu["acc_y"],
            imu["acc_z"],

            imu["gyro_x"],
            imu["gyro_y"],
            imu["gyro_z"],

            imu["angle_x"],
            imu["angle_y"],

            pe_esquerdo,
            pe_direito
        ]


        for joint in JOINTS:

            linha.append(temperaturas[joint])
            linha.append(correntes[joint])
            linha.append(posicoes[joint])
            linha.append(comandos[joint])
            linha.append(stiffnesses[joint])


        writer.writerow(linha)
        csv_file.flush()


        time.sleep(INTERVALO)


except KeyboardInterrupt:

    print("")
    print("==============================================")
    print("DIAGNOSTICO INTERROMPIDO PELO USUARIO")
    print("==============================================")


except Exception as e:

    print("")
    print("ERRO DURANTE O DIAGNOSTICO:")
    print(e)


finally:

    csv_file.close()

    print("")
    print("Arquivo salvo:")
    print(ARQUIVO_CSV)