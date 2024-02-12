import typing as _typing
import cv2
from cv2 import aruco
from enum import Enum


class ArucoProcess:

    def __init__(self, arucoSize: int, width: int, height: int) -> None:
        """Init ArucoProcess class

        Args:
            arucoSize (int): Real size in mm
            width (int): Width of the frame in pixel. e.g: 1280
            height (int): Height of the frame in pixel. e.g: 720
        """
        self.arucoSize = arucoSize
        self.arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)
        self.arucoParams = aruco.DetectorParameters()
        self.width = width
        self.height = height
        self.frame: cv2.typing.MatLike = None
        self.dico = {}

        self.TL = (1, 1)
        self.TR = (self.width - 1, 1)
        self.BL = (1, self.height - 1)
        self.BR = (self.width - 1, self.height - 1)

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

        self.dico = {}
        if ids is not None:
            for j in range(len(ids)):
                aruco_perimeter = cv2.arcLength(corners[j], True)
                pixel_cm_ratio = aruco_perimeter / 20
                actual_size = self.arucoSize / pixel_cm_ratio
                a = corners[j][0][0]
                b = corners[j][0][1]
                c = corners[j][0][2]
                d = corners[j][0][3]
                points = [a, b, c, d]
                Cx, Cy = calculer_centre(points)
                Cx -= self.width // 2
                Cy -= self.height // 2
                self.dico[ids[j][0]] = (Cx, -Cy, actual_size)

        print(self.dico.get(0) if len(self.dico) > 0 else {})

    def lines(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        """Draw HUD border lines

        Args:
            frame (cv2.typing.MatLike): Frame to work with

        Returns:
            cv2.typing.MatLike: Frame with lines drawn on it
        """
        thick = 3
        # TOP
        frame = cv2.line(
            frame,
            self.TL,
            self.TR,
            coloration(
                self.dico.get(0)[1] if not self.dico.get(0) == None else -999, True
            ),
            thick,
        )
        # BOTTOM
        frame = cv2.line(
            frame,
            self.BL,
            self.BR,
            coloration(
                self.dico.get(0)[1] if not self.dico.get(0) == None else 999, False
            ),
            thick,
        )
        # LEFT
        frame = cv2.line(
            frame,
            self.TL,
            self.BL,
            coloration(
                self.dico.get(0)[0] if not self.dico.get(0) == None else 999, False
            ),
            thick,
        )
        # RIGHT
        frame = cv2.line(
            frame,
            self.TR,
            self.BR,
            coloration(
                self.dico.get(0)[0] if not self.dico.get(0) == None else -999, True
            ),
            thick,
        )
        return frame

    def hud(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        """Put HUD on frame bebore displaying

        Args:
            frame (cv2.typing.MatLike): Frame to work with

        Returns:
            cv2.typing.MatLike: The frame with HUD applied on
        """
        frame = cv2.putText(
            self.lines(frame),
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
        c, _, frame = self.detector()

        self.hud(frame)

        cv2.imshow("ArUco Detection", frame)


def coloration(val: float, positive: bool) -> tuple[int,int,int]:
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
