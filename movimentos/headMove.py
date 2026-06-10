# Choregraphe simplified export in Python.
from naoqi import ALProxy
import time
def headMove(ver=0.0,hor=0.0):
    names = list()
    times = list()
    keys = list()

    names.append("HeadPitch")
    times.append([1])
    keys.append([0.5])

    names.append("HeadYaw")
    times.append([1])
    keys.append([hor])
    
    return names,times,keys

names  = ['HeadYaw']
stiffnessLists  = [0.25, 0.5, 1.0, 0.0]
timeLists  = [1.0, 2.0, 3.0, 4.0]

def inicializar_e_rastrear(robot_ip, port):
    try:
# uncomment the following line and modify the IP if you use this script outside Choregraphe.
        motion = ALProxy("ALMotion", str(robot_ip),int(port))
        tracker = ALProxy("ALTracker",str(robot_ip),int(port))
        motion.setStiffnesses("Head", 1.0)
        targetName = "Face"
        faceWidth = 0.5
        tracker.registerTarget(targetName, faceWidth)
        tracker.track(targetName)

        time.sleep(3)
        print(tracker.getActiveTarget())
        # motion.stiffnessInterpolation(names, stiffnessLists, timeLists)
        # commandAngles = motion.getAngles("HeadPitch",False)
        # print(commandAngles)
    except Exception as e:
        print ("Erro ao conectar com o NAO: ", e)
