import cv2
from pyparrot.DroneVision import DroneVision
from pyparrot.Minidrone import Mambo
import threading
import time


class VideoStreamOpenError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class VideoStream():
    def __init__(self, drone: Mambo, fps: int = 15, callback=None, callback_args=None) -> None:
        self.video_feed = DroneVision(drone, is_bebop=False, buffer_size=200)
        self.video_feed.fps = fps
        self.drone = drone
        ret = self.video_feed.open_video()
        if not ret:
            raise VideoStreamOpenError("Failed to open Mambo video feed")

        # Fonction callback appelée quand une nouvelle image arrive dans le flux vidéo
        # exécutée dans un thread à part donc faire attention aux accès concurrents
        if callback is not None:
            self.video_feed.set_user_callback_function(callback, callback_args)

    def next(self):
        return self.video_feed.get_latest_valid_picture()

    def close(self):
        self.video_feed.close_video()


if __name__ == "__main__":
    mambo_addr = "00:93:37:50:3B:B0"
    mambo = Mambo(mambo_addr, use_wifi=True)
    ret = mambo.connect(num_retries=3)

    if ret:
        stream = None
        try:
            stream = VideoStream(mambo)
        except VideoStreamOpenError as e:
            print(e)
        if stream is not None:
            img = stream.next()
            print(img)
            cv2.imshow('Image read', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            stream.close()
        mambo.disconnect()
