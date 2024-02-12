import cv2
import cv2.typing
import urllib.request
import numpy as np
from enum import Enum

DEBUG_CV2 = True


class URLTYPE(Enum):
    URL_LO = "http://192.168.168.143/cam-lo.jpg"
    URL_MID = "http://192.168.168.143/cam-mid.jpg"
    URL_HI = "http://192.168.168.143/cam-hi.jpg"
    URL_LIGHT = "http://192.168.168.143/led"


def urlPicker(quality: str) -> str:
    if quality == "lo":
        return URLTYPE.URL_LO.value
    if quality == "mid":
        return URLTYPE.URL_MID.value
    if quality == "hi":
        return URLTYPE.URL_HI.value


def sizePicker(quality: str) -> tuple[int, int]:
    if quality == "lo":
        return (320, 240)
    if quality == "mid":
        return (640, 480)
    if quality == "hi":
        return (1280, 720)


class WebRequester:
    def __init__(self, quality: str) -> None:
        self.url = urlPicker(quality)
        self.size = sizePicker(quality)
        self.width = self.size[0]
        self.height = self.size[1]

    def request(self) -> cv2.typing.MatLike:
        # Create a VideoCapture object & check if the IP camera stream is opened successfully
        cap = cv2.VideoCapture(self.url)
        if not cap.isOpened():
            print("Failed to open the IP camera stream")
            exit()

        # Read a frame from the video stream
        img_resp = urllib.request.urlopen(self.url)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        cap.release()

        # Decoding data
        return cv2.imdecode(imgnp, -1)
    
    def TurnOnLight(self):
        ret = urllib.request.urlopen(URLTYPE.URL_LIGHT.value)
        print(str(ret))


def ShowRequest(img: cv2.typing.MatLike):
    cv2.imshow("live Cam Testing", img)


if __name__ == "__main__":
    key = None
    requester = WebRequester("mid")

    while True:
        try:
            im = requester.request()

            if DEBUG_CV2:
                ShowRequest(im)
                key = cv2.waitKey(5)
                if key == ord("q"):
                    break

        except KeyboardInterrupt:
            break

    if DEBUG_CV2:
        cv2.destroyAllWindows()
