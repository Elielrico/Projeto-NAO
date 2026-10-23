# -*- coding: utf-8 -*-
import threading
from naoqi import ALProxy
from beijos import Beijos

IP_NAO = "169.254.179.49"
PORTA = 9559

# Conexão com o robô
motion = ALProxy("ALMotion", IP_NAO, PORTA)

IP_PC = "169.254.50.109"


def tocar_audio():
   
    url = "http://" + IP_PC + ":8000/audio"


def executar_beijos():
    # Obtém a trajetória definida em beijos.py
    names, times, keys, nome = Beijos()

    # Executa o movimento em uma thread
    thread_movimento = threading.Thread(
        target=motion.angleInterpolation,
        args=(names, keys, times, True)
    )

    # Executa o áudio em paralelo
    thread_audio = threading.Thread(
        target=tocar_audio
    )

    thread_movimento.start()
    thread_audio.start()

    # Aguarda ambos terminarem
    thread_movimento.join()
    thread_audio.join()

    print("Movimento e audio finalizados!")


if __name__ == "__main__":
    executar_beijos()
