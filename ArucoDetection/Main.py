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

from inspect import getsourcefile
from os.path import abspath
print(abspath(getsourcefile(lambda:0)))


# Uncomment to install requirements
# install()

import cv2
import cv2.aruco as aruco
import numpy as np
import time

import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 100)
voices = engine.getProperty("voices")
engine.setProperty("voice", "english")


def tell(msg: str) -> None:
    engine.say(msg)
    engine.runAndWait()


# tell("Initialization")

from ArucoProcess import ArucoProcess
from WebRequester import WebRequester, ShowRequest
from Calibration import calibrate

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
    # print(mean)
    return mean > limit


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("python Main.py (lo|mid|hi) (4|5|6|7) (size in mm) [ArucoID=0]")
    elif not sys.argv[1] in ["lo", "mid", "hi"]:
        print(f"Invalid argument : {sys.argv[1]}. Must be in [lo, mid, hi]")
        print("python Main.py (lo|mid|hi) (4|5|6|7) (size in mm) [ArucoID=0]")
    elif not int(sys.argv[2]) in [4, 5, 6, 7]:
        print(f"Invalid argument : {sys.argv[2]}. Must be in [4, 5, 6, 7]")
        print("python Main.py (lo|mid|hi) (4|5|6|7) (size in mm) [ArucoID=0]")
    elif not int(sys.argv[3]) > 0:
        print(f"Invalid argument : {sys.argv[3]}. Must be > 0")
        print("python Main.py (lo|mid|hi) (4|5|6|7) (size in mm) [ArucoID=0]")
    elif len(sys.argv) == 5 and int(sys.argv[4]) < 0:
        print(f"Invalid argument : {sys.argv[4]}. Must be > 0")
        print("python Main.py (lo|mid|hi) (4|5|6|7) (size in mm) [ArucoID=0]")
    else:
        mtx = calibrate(False)
        while True:
            try:
                requester: WebRequester = WebRequester(sys.argv[1])
                processor: ArucoProcess = ArucoProcess(
                    int(sys.argv[2]),
                    int(sys.argv[3]),
                    requester.width,
                    requester.height,
                    int(sys.argv[4]),
                )

                img = requester.request()

                if not BrightnessControl(img):
                    requester.TurnOnLight()
                    # pass

                if DEBUG_WEB:
                    ShowRequest(img)

                processor.getArucos(img)

                if DEBUG_ARUCO:
                    processor.showArucos()

                dic = processor.dico.get(processor.id)
                cx, cy, dist = dic if not dic == None else (0,0,0)
                print(cx, cy, dist)

                if(abs(cx) > 20):
                    tell("Left") if cx > 0 else tell("Right")

                if(abs(cy) > 20):
                    tell("Back") if cy > 0 else tell("Front")

                if DEBUG_WEB or DEBUG_ARUCO:
                    key = cv2.waitKey(5)
                    if key == ord("q"):
                        break

            except KeyboardInterrupt:
                break
