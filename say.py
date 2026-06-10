# -*- encoding: UTF-8 -*-
from naoqi import ALProxy

def main():
    motion = ALProxy("ALMotion","10.11.11.109", 9559)
    tts    = ALProxy("ALTextToSpeech", "10.11.11.109", 9559)
    #posição segura
    
    motion.rest()
    motion.wakeUp()
    motion.moveInit()

    tts.setParameter("speed", 85)
    tts.setParameter("pitchShift", 1.4)
    tts.setParameter("doubleVoice", 0)
    #motion.post.moveTo(0.5, 0, 0)
    #tts.say("I'm walking")
    motion.stiffnessInterpolation("Body", 1.0, 1.0)
    # Permite que o robô use os braços enquanto se move/fala
    motion.setMoveArmsEnabled(True, True) # (LeftArm, RightArm)

    animated_tts = ALProxy("ALAnimatedSpeech", "10.11.11.109", 9559)
    animated_tts.setBodyLanguageMode(2) # 2 é o modo "Contextual" (corpo todo)
    animated_tts.say("Agora eu realmente espero mover os meus braços!")
    # A tag ^mode(contextual) força o uso de braços
    animated_tts.say("^mode(contextual) Olá! Eu sou um robô e estou movendo meus braços.")
    # O robô vai mover as mãos de forma condizente com a frase
    frase = "Eu estou muito feliz em te ver hoje!"
    animated_tts.say(frase)
    animated_tts.say("Tchau")
    animated_tts.say("Olá")
    animated_tts.say("Eu vou ^start(animations/Stand/Gestures/Explain_1) explicar como eu funciono.")
if __name__ == "__main__":
    main()