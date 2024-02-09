import cv2
from cv2 import aruco


def calculer_centre(points):
    # Vérifier que la liste contient exactement 4 points
    if len(points) != 4:
        raise ValueError("La liste doit contenir exactement 4 points en 2D.")

    # Calculer les moyennes des coordonnées x et y
    cx = sum(p[0] for p in points) / 4
    cy = sum(p[1] for p in points) / 4

    # Retourner les coordonnées du centre
    return cx, cy


def GetArucoPoint(arucoDict, arucoParams, frame, width, height):
    # # Convertir l'image en niveaux de gris
    origin_size = 5.5  # cm
    aruco_perimeter = []
    pixel_cm_ratio = []
    actual_size = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # print(width,height)
    (corners, ids, _) = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
    # print(corners)
    # Nouvelle coordonnée x centrée = Ancienne coordonnée x - (Largeur de l'image / 2)
    # Nouvelle coordonnée y centrée = Ancienne coordonnée y - (Hauteur de l'image / 2)

    frame = aruco.drawDetectedMarkers(frame, corners, ids)
    dico = {}
    if ids is not None:
        for j in range(len(ids)):
            aruco_perimeter = cv2.arcLength(corners[j], True)
            pixel_cm_ratio = aruco_perimeter / 20
            actual_size = origin_size / pixel_cm_ratio
            a = corners[j][0][0]
            b = corners[j][0][1]
            c = corners[j][0][2]
            d = corners[j][0][3]
            points = [a, b, c, d]
            Cx, Cy = calculer_centre(points)
            Cx -= width // 2
            Cy -= height // 2
            dico[ids[j][0]] = (Cx, -Cy, actual_size)
    return dico


def Debug_Aruco(dict: dict, frame: cv2.typing.MatLike):
    arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    arucoParams = aruco.DetectorParameters()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    (corners, ids, _) = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
    frame = aruco.drawDetectedMarkers(frame, corners, ids)
    cv2.imshow("ArUco Detection", frame)


if __name__ == "__main__":
    arucoParams = aruco.DetectorParameters()
    arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    # Capturer la vidéo depuis la webcam (0 pour la webcam par défaut)
    cap = cv2.VideoCapture(-1)

    while True:
        # Lire une frame depuis la vidéo
        ret, frame = cap.read()
        dico = GetArucoPoint(arucoDict, arucoParams, frame, cap.get(3), cap.get(4))
        # Afficher la vidéo en direct
        print(dico)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # print(width,height)
        (corners, ids, _) = cv2.aruco.detectMarkers(
            gray, arucoDict, parameters=arucoParams
        )
        # print(corners)
        # Nouvelle coordonnée x centrée = Ancienne coordonnée x - (Largeur de l'image / 2)
        # Nouvelle coordonnée y centrée = Ancienne coordonnée y - (Hauteur de l'image / 2)

        frame = aruco.drawDetectedMarkers(frame, corners, ids)
        cv2.imshow("ArUco Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
