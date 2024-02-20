"""
This demo calculates multiple things for different scenarios.

Here are the defined reference frames:

TAG:
                A y
                |
                |
                |tag center
                O---------> x

CAMERA:


                X--------> x
                | frame center
                |
                |
                V y

F1: Flipped (180 deg) tag frame around x axis
F2: Flipped (180 deg) camera frame around x axis

The attitude of a generic frame 2 respect to a frame 1 can obtained by calculating euler(R_21.T)

We are going to obtain the following quantities:
    > from aruco library we obtain tvec and Rct, position of the tag in camera frame and attitude of the tag
    > position of the Camera in Tag axis: -R_ct.T*tvec
    > Transformation of the camera, respect to f1 (the tag flipped frame): R_cf1 = R_ct*R_tf1 = R_cf*R_f
    > Transformation of the tag, respect to f2 (the camera flipped frame): R_tf2 = Rtc*R_cf2 = R_tc*R_f
    > R_tf1 = R_cf2 an symmetric = R_f


"""

import numpy as np
import cv2
import cv2.aruco as aruco
import sys, time, math

# --- Define Tag
id_to_find = 155
marker_size = 14  # - [cm]


# ------------------------------------------------------------------------------
# ------- ROTATIONS https://www.learnopencv.com/rotation-matrix-to-euler-angles/
# ------------------------------------------------------------------------------
# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):
    assert isRotationMatrix(R)

    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])


from Calibration import calibrate

# --- Get the camera calibration path
camera_matrix, camera_distortion = calibrate(False)

# --- 180 deg rotation matrix around the x axis
R_flip = np.zeros((3, 3), dtype=np.float32)
R_flip[0, 0] = 1.0
R_flip[1, 1] = -1.0
R_flip[2, 2] = -1.0

# --- Define the aruco dictionary
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)
parameters = aruco.DetectorParameters()

import glob

images = glob.glob("**/test*.jpg", recursive=True)
images.append(images[-1])
i = 0
for image in images:

    # -- Read the camera frame
    frame = cv2.imread(image)

    if i == 2:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    i += 1

    # -- Convert in gray scale
    gray = cv2.cvtColor(
        frame, cv2.COLOR_BGR2GRAY
    )  # -- remember, OpenCV stores color images in Blue, Green, Red

    # -- Find all the aruco markers in the image
    corners, ids, rejected = aruco.detectMarkers(
        image=gray, dictionary=aruco_dict, parameters=parameters
    )

    if ids is not None and ids[0] == id_to_find:

        # -- ret = [rvec, tvec, ?]
        # -- array of rotation and position of each marker in camera frame
        # -- rvec = [[rvec_1], [rvec_2], ...]    attitude of the marker respect to camera frame
        # -- tvec = [[tvec_1], [tvec_2], ...]    position of the marker in camera frame
        ret = aruco.estimatePoseSingleMarkers(
            corners, marker_size, camera_matrix, camera_distortion
        )

        # -- Unpack the output, get only the first
        rvec, tvec = ret[0][0, 0, :], ret[1][0, 0, :]

        # -- Draw the detected marker and put a reference frame over it
        aruco.drawDetectedMarkers(frame, corners)
        cv2.drawFrameAxes(frame, camera_matrix, camera_distortion, rvec, tvec, 0.01)

        # -- Print the tag position in camera frame
        str_position = "MARKER Position x=%4.0f  y=%4.0f  z=%4.0f" % (
            tvec[0],
            tvec[1],
            tvec[2],
        )
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            frame, str_position, (0, 25), font, 0.4, (0, 255, 0), 1, cv2.LINE_AA
        )

        # -- Obtain the rotation matrix tag->camera
        R_ct = np.matrix(cv2.Rodrigues(rvec)[0])
        R_tc = R_ct.T

        # -- Get the attitude in terms of euler 321 (Needs to be flipped first)
        roll_marker, pitch_marker, yaw_marker = rotationMatrixToEulerAngles(
            R_flip * R_tc
        )

        # -- Print the marker's attitude respect to camera frame
        str_attitude = "MARKER Attitude r=%4.0f  p=%4.0f  y=%4.0f" % (
            math.degrees(roll_marker),
            math.degrees(pitch_marker),
            math.degrees(yaw_marker),
        )
        cv2.putText(
            frame, str_attitude, (0, 50), font, 0.4, (0, 255, 0), 1, cv2.LINE_AA
        )

        # -- Now get Position and attitude f the camera respect to the marker
        pos_camera = -R_tc * np.matrix(tvec).T

        str_position = "CAMERA Position x=%4.0f  y=%4.0f  z=%4.0f" % (
            pos_camera[0],
            pos_camera[1],
            pos_camera[2],
        )
        cv2.putText(
            frame, str_position, (0, 125), font, 0.4, (0, 255, 0), 1, cv2.LINE_AA
        )

        # -- Get the attitude of the camera respect to the frame
        roll_camera, pitch_camera, yaw_camera = rotationMatrixToEulerAngles(
            R_flip * R_tc
        )
        str_attitude = "CAMERA Attitude r=%4.0f  p=%4.0f  y=%4.0f" % (
            math.degrees(roll_camera),
            math.degrees(pitch_camera),
            math.degrees(yaw_camera),
        )
        cv2.putText(
            frame, str_attitude, (0, 150), font, 0.4, (0, 255, 0), 1, cv2.LINE_AA
        )

    # --- Display the frame
    cv2.imshow(f"frame {i}", frame)

    # --- use 'q' to quit
    key = cv2.waitKey(0)
    if key == ord("q"):
        cv2.destroyAllWindows()
        break

cv2.destroyAllWindows()
