from pyparrot.Bebop import Bebop
# from pyparrot.Minidrone import Mambo
import tkinter as tk
from PIL import Image, ImageTk
import time
import sys
import cv2
import numpy as np

from ArucoProcess import ArucoProcess
from WebRequester import WebRequester, ShowRequest
from Calibration import calibrate

SAVED = time.time()
LED = False
ELECTRO = False
DEBUG = True

class Parrot(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=500, height=500)
        self.info = tk.Label(
            self,
            text="Z : Front - S : Back\nQ : Left - D : Right\nA : Rotate Left - E : Rotate Right\nR : Up - F : Down\nEspace : Take Off - Ctrl : Land\nEscape : Panic Button\nL : Auto Land on ceiling",
        )
        self.info.pack()
        self.label = tk.Label(self, text="last key pressed:  ", width=20)
        self.label.pack(fill="both", padx=100, pady=100)
        # self.start = int(time())
        # self.timer = tk.Label(self, text=f"Time : {0.0}")
        # self.timer.pack()
        self.aruco = tk.Label(self, text=f"Aruco : Not Found")
        self.aruco.pack()

        self.label.bind("<z>", self.on_wasd)
        self.label.bind("<q>", self.on_wasd)
        self.label.bind("<s>", self.on_wasd)
        self.label.bind("<d>", self.on_wasd)
        self.label.bind("<r>", self.on_wasd)
        self.label.bind("<f>", self.on_wasd)
        self.label.bind("<a>", self.on_wasd)
        self.label.bind("<e>", self.on_wasd)
        self.label.bind("<l>", self.on_wasd)
        self.label.bind("<space>", self.on_wasd)
        self.label.bind("<Control_L>", self.on_wasd)
        self.label.bind("<Escape>", self.on_wasd)

        # give keyboard focus to the label by default, and whenever
        # the user clicks on it
        self.label.focus_set()
        self.label.bind("<1>", lambda event: self.label.focus_set())

    # def clock(self):
    #     self.timer.config(text=f"Time : {int(time()) - self.start}")
    #     self.timer.after(1, self.clock)

    def detectAruco(self):
        txt = "Found" if processor.arucoDetected(requester.request()) else "Not Found"
        self.aruco.config(text=f"Aruco : {txt}")
        self.aruco.after(1000, self.detectAruco)

    def on_wasd(self, event):
        # self.label.configure(text="last key pressed: " + event.keysym)
        match event.keysym:
            case "l":  # L
                # print("autoland ceiling")
                try:
                    autoland()
                except KeyboardInterrupt:
                    pass
                # TODO
            case "space":  # Space
                # print("taking off!")
                bebop.safe_takeoff(2)
            case "Control_L":  # Ctrl
                # print("landing")
                bebop.safe_land(2)
                bebop.smart_sleep(2)
            case "Escape":  # Panic Button
                # print("Panic Button Pushed")
                # print("Force landing")
                bebop.safe_land(2)
                bebop.smart_sleep(2)
                # print("Disconnect")
                bebop.disconnect()
                root.quit()
            case "r":  # R
                # print("Flying direct: going up")
                bebop.fly_direct(
                    roll=0, pitch=0, yaw=0, vertical_movement=10, duration=time_t
                )
            case "f":  # F
                # print("Flying direct: going down")
                bebop.fly_direct(
                    roll=0, pitch=0, yaw=0, vertical_movement=-10, duration=time_t
                )
            case "d":  # D
                # print("Flying direct: going left")
                bebop.fly_direct(
                    roll=strengh_H, pitch=0, yaw=0, vertical_movement=0, duration=time_t
                )
            case "q":  # Q
                # print("Flying direct: going right")
                bebop.fly_direct(
                    roll=-strengh_H,
                    pitch=0,
                    yaw=0,
                    vertical_movement=0,
                    duration=time_t,
                )
            case "z":  # Z
                # print("Flying direct: going forward")
                bebop.fly_direct(
                    roll=0, pitch=strengh_H, yaw=0, vertical_movement=0, duration=time_t
                )
            case "s":  # S
                # print("Flying direct: going backward")
                bebop.fly_direct(
                    roll=0,
                    pitch=-strengh_H,
                    yaw=0,
                    vertical_movement=0,
                    duration=time_t,
                )
            case "a":  # A
                # print("Flying direct: turning left")
                bebop.fly_direct(
                    roll=0, pitch=0, yaw=-strengh_H, vertical_movement=0, duration=time_t
                )
                # mambo.turn_degrees(-10)
            case "e":  # E
                # print("Flying direct: turning right")
                bebop.fly_direct(
                    roll=0, pitch=0, yaw=strengh_H, vertical_movement=0, duration=time_t
                )
                # mambo.turn_degrees(10)
        # print("flying state is %s" % mambo.sensors.flying_state)
        bebop.ask_for_state_update()

def BrightnessControl(image) -> bool:
    global SAVED
    now = time.time()
    if int(now - SAVED) < 5:
        return True
    else:
        SAVED = now
    limit = 50
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean = np.mean(gray)
    return mean > limit

def autoland():
    prev = 999
    while True:
        try :
            img = requester.request()
            processor.getArucos(img)

            if DEBUG:
                processor.showArucos()

            dic = processor.dico.get(processor.id2, processor.dico.get(processor.id1))
            cx, cy, rotZ, dist = dic if not dic == None else (0, 0, 0, 0)
            prev = (cx, cy, rotZ, dist) if dist != 0 else prev

            if processor.id2 in processor.dico and not ELECTRO:
                requester.TurnOnElectro()
                ELECTRO = True

            print(prev)
            if abs(rotZ) > 10:
                print("Rotate Left") if rotZ < 0 else print("Rotate Right")
                bebop.fly_direct(roll=0, pitch=0, yaw=-strengh_L, vertical_movement=0, duration=time_t) if rotZ < 0 else bebop.fly_direct(roll=0, pitch=0, yaw=strengh_L, vertical_movement=0, duration=time_t)
                bebop.ask_for_state_update()

            elif abs(cx) > 20 or abs(cy) > 20:
                if abs(cx) > 20:
                    print("Left") if cx > 0 else print("Right")
                    bebop.fly_direct(roll=-strengh_L, pitch=0, yaw=0, vertical_movement=0, duration=time_t) if cx > 0 else bebop.fly_direct(roll=strengh_L, pitch=0, yaw=0, vertical_movement=0, duration=time_t)
                    bebop.ask_for_state_update()
                    
                if abs(cy) > 20:
                    print("Back") if cy > 0 else print("Front")
                    bebop.fly_direct(roll=0, pitch=-strengh_L, yaw=0, vertical_movement=0, duration=time_t) if cy > 0 else bebop.fly_direct(roll=0, pitch=strengh_L, yaw=0, vertical_movement=0, duration=time_t)
                    bebop.ask_for_state_update()

            elif not dic == None :
                print("Up")
                bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=5, duration=time_t)
                bebop.ask_for_state_update()

            else:
                print("Hold")

            # TODO: EXIT CONDITION
        except KeyboardInterrupt:
            break


if __name__ == "__main__":

    camera_matrix, camera_distortion = calibrate(False)
    
    requester: WebRequester = WebRequester("mid")
    processor: ArucoProcess = ArucoProcess(
        camera_matrix,
        camera_distortion,
        6,
        100,
        requester.width,
        requester.height,
        81,
    )

    root = tk.Tk()
    time_t = 0.1
    strengh_H = 20
    strengh_L = 10
    parr = Parrot(root)
    parr.pack(fill="both", expand=True)

    # you will need to change this to the address of YOUR mambo
    # mamboAddr = "e0:14:d0:63:3d:d0"

    # make my mambo object
    # remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
    bebop = Bebop(drone_type="Bebop")

    print("trying to connect")
    success = bebop.connect(10)
    # success = True
    print("connected: %s" % success)
    if success:
        try:
            print("sleeping")
            bebop.ask_for_state_update()
            bebop.smart_sleep(2)

            # parr.clock()
            parr.detectAruco()
            root.mainloop()

        except KeyboardInterrupt:
            print("disconnect")
            bebop.safe_land(2)
            bebop.smart_sleep(2)
            bebop.disconnect()
