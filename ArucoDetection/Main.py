import subprocess
import sys

DEBUG_WEB = False
DEBUG_ARUCO = True

def install():
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "ArucoDetection/requirements.txt"]
    )

# Uncomment to install requirements
# install()

import cv2
import cv2.aruco as aruco

from ArucoProcess import GetArucoPoint, Debug_Aruco
from WebRequester import URLTYPE, WebRequester, ShowRequest

QUALITY = "mid"  # [lo|mid|hi]

arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
arucoParams = aruco.DetectorParameters()

if __name__ == "__main__":
    while True:
        try:
            requester: WebRequester = WebRequester(QUALITY)

            img = requester.request()

            if DEBUG_WEB :
                ShowRequest(img)
            
            myDict = GetArucoPoint(arucoDict, arucoParams, img, requester.size[0], requester.size[1])

            if DEBUG_ARUCO:
                Debug_Aruco(myDict, img)
            
            if DEBUG_WEB or DEBUG_ARUCO:
                key = cv2.waitKey(5)
                if key == ord("q"):
                    break

        except KeyboardInterrupt:
            break
