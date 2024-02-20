import cv2
from cv2 import aruco
import numpy as np
import os
import glob
import sys

from Calibration import calibrate

arucoType = aruco.DICT_5X5_1000
arucoSize = 140  # mm

arucoDict = aruco.getPredefinedDictionary(arucoType)
arucoParams = aruco.DetectorParameters()

images = glob.glob("**/test*.jpg", recursive=True)
print(images)
i=0
for frame in images:
    img = cv2.imread(frame)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (corners, ids, _) = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)

    display = aruco.drawDetectedMarkers(img, corners, ids)
    cv2.imshow("test Rotation", display)
    cv2.waitKey(0)

    mtx, dist = calibrate(False)

    rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(
        corners[0], 0.02, mtx, dist
    )

    print(rvec)

    display = cv2.drawFrameAxes(display, mtx, dist, rvec, tvec, 0.01)
    # display = aruco.drawAxis(display, mtx, dist, rvec, tvec, 0.01) 

    display = cv2.putText(
            display,
            f"{rvec}",
            (3, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    cv2.imshow(f"test Rotation {i}", display)
    cv2.waitKey(0)
    i+=1


cv2.destroyAllWindows()
