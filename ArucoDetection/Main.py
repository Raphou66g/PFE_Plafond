# from Displacement import *
from VideoStream import *
from videoaruco import *
import cv2.aruco as aruco

if __name__ == "__main__":
    time = 0.1
    strengh = 30
    mambo_addr = "00:93:37:50:3B:B0"
    mambo = Mambo(mambo_addr, use_wifi=True)
    ret = mambo.connect(num_retries=3)

    if ret:
        stream = None
        try:
            stream = VideoStream(mambo, fps=5)
        except VideoStreamOpenError as e:
            print(e)
        if stream is not None:
            try:
                while True:
                    img = stream.next()
                    arucoParams = aruco.DetectorParameters()
                    arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
                    dico : dict[str, tuple[float, float, float]] = GetArucoPoint(arucoDict, arucoParams, img, img.shape[0], img.shape[1])
                    if dico:
                        target = dico[0]
                        x = target[0]
                        y = target[1]
                        z = target[2]

                        if x < 0:
                            print("Flying direct: going up")
                            mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=10, duration=time)
                        else :
                            print("Flying direct: going down")
                            mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=-10, duration=time)

                        if y < 0:
                            print("Flying direct: going right")
                            mambo.fly_direct(
                                roll=strengh, pitch=0, yaw=0, vertical_movement=0, duration=time
                            )
                        else:
                            print("Flying direct: going left")
                            mambo.fly_direct(
                                roll=-strengh, pitch=0, yaw=0, vertical_movement=0, duration=time
                            )

                        if z < 0:
                            print("Flying direct: going backward")
                            mambo.fly_direct(
                                roll=0, pitch=-strengh, yaw=0, vertical_movement=0, duration=time
                            )
                        else:
                            print("Flying direct: going forward")
                            mambo.fly_direct(
                                roll=0, pitch=strengh, yaw=0, vertical_movement=0, duration=time
                            )
            except KeyboardInterrupt:
                stream.close()
        mambo.disconnect()
