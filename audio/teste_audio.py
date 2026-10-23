from naoqi import ALProxy

IP = "169.254.179.49"
PORTA = 9559

# Troque pelo IPv4 do Windows
IP_PC = "169.254.50.109"

audio = ALProxy("ALAudioPlayer", IP, PORTA)

url = "http://" + IP_PC + ":8000/audio"

audio.playWebStream(url, 1.0, 0.0)

