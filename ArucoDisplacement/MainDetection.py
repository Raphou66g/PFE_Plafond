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

print(abspath(getsourcefile(lambda: 0)))


# Uncomment to install requirements
# install()

import cv2
import numpy as np
import cv2.aruco as aruco
import time

from ArucoProcess import ArucoProcess
from WebRequester import WebRequester, ShowRequest
from Calibration import calibrate

SAVED = time.time()
LED = False
ELECTRO = False


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
    def print_usage_message():
        print("python Main.py (lo|mid|hi) [4|5|6|7] [Big size in mm] [Small size in mm] [ArucoID1=81] [ArucoID2=88]")

    def print_invalid_argument_message(argument, valid_values, condition=None):
        message = f"Invalid argument : {argument}. Must be in {valid_values}"
        if condition is not None:
            message += f" and {condition}"
        # print(message)
        print_usage_message()

    def check_argument_value(argument, valid_values, condition=None):
        if argument not in valid_values:
            print_invalid_argument_message(argument, valid_values, condition)
            return False
        return True

    def check_positive_float_argument(argument):
        try:
            value = float(argument)
            if value <= 0:
                raise ValueError
        except ValueError:
            print_invalid_argument_message(argument, "positive float")
            return False
        return True

    def check_non_negative_integer_argument(argument):
        if not argument.isdigit() or int(argument) < 0:
            print_invalid_argument_message(argument, "non-negative integer")
            return False
        return True

    if len(sys.argv) < 2:
        print_usage_message()
    elif not check_argument_value(sys.argv[1], ["lo", "mid", "hi"]):
        pass
    elif len(sys.argv) >= 3 and not check_argument_value(sys.argv[2], ["4", "5", "6", "7"]):
        pass
    elif len(sys.argv) >= 4 and not check_positive_float_argument(sys.argv[3]):
        pass
    elif len(sys.argv) >= 5 and not check_positive_float_argument(sys.argv[4]):
        pass
    elif len(sys.argv) >= 6 and not check_non_negative_integer_argument(sys.argv[5]):
        pass
    elif len(sys.argv) >= 7 and not check_non_negative_integer_argument(sys.argv[6]):
        pass
    else:
        camera_matrix, camera_distortion = calibrate(False)
        prev = 999
        requester: WebRequester = WebRequester(sys.argv[1])
        processor: ArucoProcess = ArucoProcess(
            matrix=camera_matrix,
            distortion=camera_distortion,
            width=requester.width,
            height=requester.height,
            arucoType= int(sys.argv[2]) if len(sys.argv) >= 3 else 6,
            arucoSize1= float(sys.argv[3]) if len(sys.argv) >= 4 else 100,
            arucoSize2= float(sys.argv[4]) if len(sys.argv) >= 5 else 12.5,
            id1 = int(sys.argv[5]) if len(sys.argv) >= 6 else 81,
            id2 = int(sys.argv[6]) if len(sys.argv) >= 7 else 88
        )
        while True:
            try:

                img = requester.request()

                # if not BrightnessControl(img) and not LED:
                #     requester.TurnOnLight()
                #     LED = True
                # pass

                if DEBUG_WEB:
                    ShowRequest(img)

                processor.getArucos(img)

                if DEBUG_ARUCO:
                    processor.showArucos()

                dic = processor.dico.get(processor.id2, processor.dico.get(processor.id1))
                cx, cy, rotZ, dist = dic if not dic == None else (0, 0, 0, 0)
                prev = (cx, cy, rotZ, dist) if dist != 0 else prev

                if processor.id2 in processor.dico and not ELECTRO:
                    requester.TurnOnElectro()
                    ELECTRO = True

                if DEBUG_ARUCO:
                    # print("\n")
                    # print(prev)
                    if abs(rotZ) > 5:
                        # tell("Rotate Left") if rotZ < 0 else tell("Rotate Right")
                        print("Rotate Left") if rotZ < 0 else print("Rotate Right")
                    elif abs(cx) > 20 or abs(cy) > 20:
                        if abs(cx) > 20:
                            # tell("Left") if cx > 0 else tell("Right")
                            print("Left") if cx > 0 else print("Right")

                        if abs(cy) > 20:
                            # tell("Back") if cy > 0 else tell("Front")
                            print("Back") if cy > 0 else print("Front")
                    elif not dic == None:
                        # tell("Up")
                        print("Up")
                    else:
                        # tell("Hold")
                        print("Hold")

                if DEBUG_WEB or DEBUG_ARUCO:
                    key = cv2.waitKey(5)
                    if key == ord("q"):
                        requester.TurnOffLight()
                        break

            except KeyboardInterrupt:
                break
