import cv2
import numpy as np
import os
import glob
import sys
from enum import Enum
from WebRequester import WebRequester

from inspect import getsourcefile
from os.path import abspath
print(abspath(getsourcefile(lambda:0)))

def calibrate(display:bool) -> tuple[cv2.typing.MatLike, cv2.typing.MatLike]:
    # Defining the dimensions of checkerboard
    CHECKERBOARD = (6, 9)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = []


    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0, :, :2] = np.mgrid[0 : CHECKERBOARD[0], 0 : CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    # Extracting path of individual image stored in a given directory
    images = glob.glob("**/Capture_*.jpg", recursive=True)
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        ret, corners = cv2.findChessboardCorners(
            gray,
            CHECKERBOARD,
            cv2.CALIB_CB_ADAPTIVE_THRESH
            + cv2.CALIB_CB_FAST_CHECK
            + cv2.CALIB_CB_NORMALIZE_IMAGE,
        )

        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display 
        them on the images of checker board
        """
        if ret == True:
            objpoints.append(objp)
            # refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            imgpoints.append(corners2)

        if display:
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
            cv2.imshow("img", img)
            cv2.waitKey(0)

    if display:
        cv2.destroyAllWindows()

    # h, w = img.shape[:2]

    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    if display:
        print("\nError in projection : ", ret) 
        print("\nCamera matrix :")
        print(mtx)
        print("\ndist :")
        print(dist)
        print("\nrvecs :")
        print(rvecs)
        print("\ntvecs :")
        print(tvecs)
    
    return mtx, dist


class CALIBRATION_MODE(Enum):
    CAPTURE = 0
    PROCESS = 1


def capName(number) -> str:
    if number < 10:
        return f"Capture_00{number}"
    elif number < 100:
        return f"Capture_0{number}"
    else:
        return f"Capture_{number}"


if __name__ == "__main__":
    mode = None
    if len(sys.argv) <= 1 or sys.argv[1].lower() not in ["capture", "process"]:
        print("python Calibration.py (capture|process)")
    else:
        mode = CALIBRATION_MODE.CAPTURE if sys.argv[1].lower() == "capture" else CALIBRATION_MODE.PROCESS

    if mode == CALIBRATION_MODE.CAPTURE:
        requester = WebRequester("lo")
        num = 1
        while True:
            im = requester.request()
            cv2.imshow("live Cam Capturing", im)
            key = cv2.waitKey(5)
            if key == ord("q"):
                break
            elif key == ord("s"):
                name = f"**/Images/{capName(num)}.jpg"
                cv2.imwrite(name, im)
                num += 1
        cv2.destroyAllWindows()
    elif mode == CALIBRATION_MODE.PROCESS:
        calibrate(True)