import typing as _typing
import cv2
from cv2 import aruco
import numpy as np
import math


class ArucoProcess:

    def __init__(
        self,
        matrix: cv2.typing.MatLike,
        distortion: cv2.typing.MatLike,
        width: int,
        height: int,
        arucoType: int = 6,
        arucoSize1: float = 100,
        arucoSize2: float = 12.5,
        id1: int = 81,
        id2: int = 88,
    ) -> None:
        """Init ArucoProcess class

        Args:
            matrix (cv2.typing.MatLike): Camera matrix retrieve by the calibration
            distortion (cv2.typing.MatLike): Camera distortion retrieve by the calibration
            width (int): Width of the frame in pixel. e.g: 1280
            height (int): Height of the frame in pixel. e.g: 720
            arucoType (int, optional): int x int type. Defaults to 6.
            arucoSize1 (int, optional): Big ArUco real size in mm. Defaults to 100 (mm).
            arucoSize2 (int, optional): Small ArUco real size in mm. Defaults to 12.5 (mm).
            id1 (int, optional): ID of the biggest searched ArUco. Defaults to 81.
            id2 (int, optional): ID of the smallest searched ArUco. Defaults to 88.
        """
        self.matrix = matrix
        self.distortion = distortion
        self.arucoType = (
            aruco.DICT_4X4_1000
            if arucoType == 4
            else (
                aruco.DICT_5X5_1000
                if arucoType == 5
                else aruco.DICT_6X6_1000 if arucoType == 6 else aruco.DICT_7X7_1000
            )
        )
        self.arucoSize1 = arucoSize1
        self.arucoSize2 = arucoSize2
        self.arucoDict = aruco.getPredefinedDictionary(self.arucoType)
        self.arucoParams = aruco.DetectorParameters()
        self.width = width
        self.height = height
        self.id1 = id1
        self.id2 = id2
        self.frame: cv2.typing.MatLike = None
        self.dico = {}
        self.rotaZion = 0

        # self.TL = (1, 1)
        # self.TR = (self.width - 1, 1)
        # self.BL = (1, self.height - 1)
        # self.BR = (self.width - 1, self.height - 1)

    def grayOut(self) -> cv2.typing.MatLike:
        """Return grayscale of the frame

        Returns:
            Matlike: Grayscale of the frame
        """
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def detector(
        self,
    ) -> tuple[
        _typing.Sequence[cv2.typing.MatLike], cv2.typing.MatLike, cv2.typing.MatLike
    ]:
        """Looking for ArUco and mark them on frame

        Returns:
            tuple[_typing.Sequence[cv2.typing.MatLike], cv2.typing.MatLike, cv2.typing.MatLike]: ArUco corners, ids and the frame with markers on it
        """
        (corners, ids, _) = cv2.aruco.detectMarkers(
            self.grayOut(), self.arucoDict, parameters=self.arucoParams
        )
        return corners, ids, aruco.drawDetectedMarkers(self.frame, corners, ids)

    def getPos(self, frame, corners, arID):
        # --- 180 deg rotation matrix around the x axis
        R_flip = np.zeros((3, 3), dtype=np.float32)
        R_flip[0, 0] = 1.0
        R_flip[1, 1] = -1.0
        R_flip[2, 2] = -1.0

        ret = aruco.estimatePoseSingleMarkers(
            corners,
            self.arucoSize1 / 10 if arID == self.id1 else self.arucoSize2 / 10,
            self.matrix,
            self.distortion,
        )
        rvec, tvec = ret[0][0, 0, :], ret[1][0, 0, :]
        cv2.drawFrameAxes(frame, self.matrix, self.distortion, rvec, tvec, 1)

        R_ct = np.matrix(cv2.Rodrigues(rvec)[0])
        R_tc = R_ct.T
        roll_marker, pitch_marker, yaw_marker = rotationMatrixToEulerAngles(
            R_flip * R_tc
        )
        self.rotaZion = math.degrees(yaw_marker)

    def arucoDetected(self, frame):
        self.frame = frame
        _, ids, _ = self.detector()
        if ids == None:
            return False
        return self.id1 in ids or self.id2 in ids

    def getArucos(self, frame: cv2.typing.MatLike) -> None:
        """Retreive ArUcos and data on them and save it into self.dico

        Args:
            frame (cv2.typing.MatLike): Frame from the cam
        """
        self.frame = frame
        aruco_perimeter = []
        pixel_cm_ratio = []
        actual_size = []

        corners, ids, _ = self.detector()
        # print(ids)

        self.dico = {}
        if ids == None:
            return
        for j in range(len(ids)):
            # print(f"curr : {ids[j]} : {88 in ids[j]}")
            is81 = self.id1 in ids[j]
            is88 = self.id2 in ids[j]
            if not is81 and not is88 :
                return
            aruco_perimeter = cv2.arcLength(corners[j], True)
            pixel_cm_ratio = aruco_perimeter / 20
            size = (self.arucoSize1 if is81 else self.arucoSize2) / 10
            actual_size = size / pixel_cm_ratio
            a = corners[j][0][0]
            b = corners[j][0][1]
            c = corners[j][0][2]
            d = corners[j][0][3]
            points = [a, b, c, d]
            Cx, Cy = calculer_centre(points)
            Cx -= self.width // 2
            Cy -= self.height // 2

            if is81 or is88:
                self.getPos(frame, corners, self.id2 if is88 else self.id1)

            self.dico[ids[j][0]] = (
                Cx,
                -Cy,
                self.rotaZion,
                actual_size,
            )

        # print(self.dico.get(self.id) if self.id in self.dico.keys() else {})

    # def lines(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
    #     """Draw HUD border lines

    #     Args:
    #         frame (cv2.typing.MatLike): Frame to work with

    #     Returns:
    #         cv2.typing.MatLike: Frame with lines drawn on it
    #     """
    #     thick = 3
    #     # TOP
    #     frame = cv2.line(
    #         frame,
    #         self.TL,
    #         self.TR,
    #         coloration(
    #             (
    #                 self.dico.get(self.id)[1]
    #                 if not self.dico.get(self.id) == None
    #                 else -999
    #             ),
    #             True,
    #         ),
    #         thick,
    #     )
    #     # BOTTOM
    #     frame = cv2.line(
    #         frame,
    #         self.BL,
    #         self.BR,
    #         coloration(
    #             (
    #                 self.dico.get(self.id)[1]
    #                 if not self.dico.get(self.id) == None
    #                 else 999
    #             ),
    #             False,
    #         ),
    #         thick,
    #     )
    #     # LEFT
    #     frame = cv2.line(
    #         frame,
    #         self.TL,
    #         self.BL,
    #         coloration(
    #             (
    #                 self.dico.get(self.id)[0]
    #                 if not self.dico.get(self.id) == None
    #                 else 999
    #             ),
    #             False,
    #         ),
    #         thick,
    #     )
    #     # RIGHT
    #     frame = cv2.line(
    #         frame,
    #         self.TR,
    #         self.BR,
    #         coloration(
    #             (
    #                 self.dico.get(self.id)[0]
    #                 if not self.dico.get(self.id) == None
    #                 else -999
    #             ),
    #             True,
    #         ),
    #         thick,
    #     )
    #     return frame

    def hud(self, frame: cv2.typing.MatLike) -> None:
        """Put HUD on frame bebore displaying

        Args:
            frame (cv2.typing.MatLike): Frame to work with
        """
        cv2.putText(
            frame,
            f"{self.dico}",
            (3, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    def showArucos(self):
        """Display the captured frame with ArUco marked"""
        _, _, frame = self.detector()

        self.hud(frame)

        cv2.imshow("ArUco Detection", frame)


def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


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


def coloration(val: float, positive: bool) -> tuple[int, int, int]:
    """Return Scalar for border lines coloration

    Args:
        val (float): center pos of the ArUco
        positive (bool): is the value must be positive (top or right side) ?

    Returns:
        tuple[int,int,int]: color scalar in BGR order
    """
    red = 0
    green = 255
    soft = 30
    hard = 60
    if (positive and val >= 0) or (not positive and val < 0):
        if val > hard or val < -hard:
            return (255, 0, 255)
        elif val <= soft and val >= -soft:
            red = int(val * 255 / soft) if positive else int(-val * 255 / soft)
            return (0, green, red)
        else:
            red = 255
            green -= int(val * 255 / hard) if positive else int(-val * 255 / hard)
            return (0, green, red)
    elif val > 100 or val < -100:
        return (0, 0, 0)
    else:
        return (0, green, red)


def calculer_centre(points: list) -> tuple[float, float]:
    """Calculate aruco center pos

    Args:
        points (list): Corners positions in 2D

    Raises:
        ValueError: list must contain 4 values

    Returns:
        tuple[float, float]: Center position X & Y
    """

    # Vérifier que la liste contient exactement 4 points
    if len(points) != 4:
        raise ValueError("La liste doit contenir exactement 4 points en 2D.")

    # Calculer les moyennes des coordonnées x et y
    cx = sum(p[0] for p in points) / 4
    cy = sum(p[1] for p in points) / 4

    # Retourner les coordonnées du centre
    return cx, cy


# if __name__ == "__main__":
#     arucoParams = aruco.DetectorParameters()
#     arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
#     # Capturer la vidéo depuis la webcam (0 pour la webcam par défaut)
#     cap = cv2.VideoCapture(-1)

#     while True:
#         # Lire une frame depuis la vidéo
#         ret, frame = cap.read()
#         dico = GetArucoPoint(arucoDict, arucoParams, frame, cap.get(3), cap.get(4))
#         # Afficher la vidéo en direct
#         print(dico)
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         # print(width,height)
#         (corners, ids, _) = cv2.aruco.detectMarkers(
#             gray, arucoDict, parameters=arucoParams
#         )
#         # print(corners)
#         # Nouvelle coordonnée x centrée = Ancienne coordonnée x - (Largeur de l'image / 2)
#         # Nouvelle coordonnée y centrée = Ancienne coordonnée y - (Hauteur de l'image / 2)

#         frame = aruco.drawDetectedMarkers(frame, corners, ids)
#         cv2.imshow("ArUco Detection", frame)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
