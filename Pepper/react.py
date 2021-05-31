from naoqi import ALProxy
import time
import qi

tts = ALProxy("ALTextToSpeech", "localhost", 9559)
session = qi.Session()
session.connect("tcp://localhost:" + str(9559))


def recact(feedback, compensation):
    if feedback == "D2":
        tts.say("speed feedback")
    else:
        tts.say("compensation feedback")
        time.sleep(1)
        # behaviour_manager = session.service("ALBehaviorManager")
        # names = behaviour_manager.getInstalledBehaviors()
        # behaviour_manager.runBehavior("behavior_1", _async=True)
        # time.sleep(0.5)
        # print names
        if compensation == "trunk-flex":
            tts.say("trunk-flex")
        if compensation == "scapular-e":
            tts.say("scapular-e")
        if compensation == "scapular-r":
            tts.say("scapular-r")
        if compensation == "elbow-flex":
            tts.say("elbow-flex")
        if compensation == "shoulder-flex":
            tts.say("shoulder-flex")
        if compensation == "distal-dys-syn":
            tts.say("distal-dys-syn")


#
# # recact("H2", "shoulder-flex")
# tts.say("fuck everybody")
