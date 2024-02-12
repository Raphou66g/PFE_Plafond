import subprocess
import sys

DEBUG_ARUCO = True
DEBUG_WEB = False and not DEBUG_ARUCO


def install():
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "ArucoDetection/requirements.txt",
        ]
    )


# Uncomment to install requirements
# install()

import cv2
import cv2.aruco as aruco
import numpy as np
import time

import pyttsx3
engine = pyttsx3.init()

engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# engine.say("I will speak this text")
# engine.runAndWait()

from ArucoProcess import ArucoProcess
from WebRequester import WebRequester, ShowRequest

SAVED = time.time()

def BrightnessControl(image) -> bool:
    global SAVED
    now = time.time()
    if int(now - SAVED) < 5:
        return True
    else:
        SAVED = now
    limit = 50
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean = np.mean(gray)
    print(mean)
    return mean > limit


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python Main.py (lo|mid|hi)")
    elif not sys.argv[1] in ["lo", "mid", "hi"]:
        print(f"Invalid argument : {sys.argv[1]}")
        print("python Main.py (lo|mid|hi)")
    else:
        while True:
            try:
                requester: WebRequester = WebRequester(sys.argv[1])
                processor: ArucoProcess = ArucoProcess(100, requester.width, requester.height)

                img = requester.request()

                if not BrightnessControl(img):
                    #requester.TurnOnLight()
                    pass

                if DEBUG_WEB:
                    ShowRequest(img)

                arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)
                arucoParams = aruco.DetectorParameters()
                processor.getArucos(img)

                if DEBUG_ARUCO:
                    processor.showArucos()

                if DEBUG_WEB or DEBUG_ARUCO:
                    key = cv2.waitKey(5)
                    if key == ord("q"):
                        break

            except KeyboardInterrupt:
                break
