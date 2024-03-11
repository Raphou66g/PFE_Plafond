from pyparrot.Minidrone import Mambo
import tkinter as tk
from PIL import Image, ImageTk
from time import time

class Parrot(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=500, height=500)
        self.info = tk.Label(self,text="Z : Front - S : Back\nQ : Left - D : Right\nA : Rotate Left - E : Rotate Right\nR : Up - F : Down\nEspace : Take Off - Ctrl : Land\nEscape : Panic Button")
        self.info.pack()
        self.label = tk.Label(self, text="last key pressed:  ", width=20)
        self.label.pack(fill="both", padx=100, pady=100)
        self.start = int(time())
        self.timer = tk.Label(self, text=f"Time : {0.0}")
        self.timer.pack()

        self.label.bind("<z>", self.on_wasd)
        self.label.bind("<q>", self.on_wasd)
        self.label.bind("<s>", self.on_wasd)
        self.label.bind("<d>", self.on_wasd)
        self.label.bind("<r>", self.on_wasd)
        self.label.bind("<f>", self.on_wasd)
        self.label.bind("<a>", self.on_wasd)
        self.label.bind("<e>", self.on_wasd)
        self.label.bind("<space>", self.on_wasd)
        self.label.bind("<Control_L>", self.on_wasd)
        self.label.bind("<Escape>", self.on_wasd)

        # give keyboard focus to the label by default, and whenever
        # the user clicks on it
        self.label.focus_set()
        self.label.bind("<1>", lambda event: self.label.focus_set())

    def clock(self):
        self.timer.config(text=f"Time : {int(time()) - self.start}")
        self.timer.after(1, self.clock)

    def on_wasd(self, event):
        self.label.configure(text="last key pressed: " + event.keysym)
        match event.keysym:
            case "space":  # Space
                print("taking off!")
                mambo.safe_takeoff(2)
            case "Control_L":  # Ctrl
                print("landing")
                mambo.safe_land(2)
                mambo.smart_sleep(2)
            case "Escape":  # Panic Button
                print("Panic Button Pushed")
                print("Force landing")
                mambo.safe_land(2)
                mambo.smart_sleep(2)
                print("Disconnect")
                mambo.disconnect()
                root.quit()
            case "r":  # R
                print("Flying direct: going up")
                mambo.fly_direct(
                    roll=0, pitch=0, yaw=0, vertical_movement=10, duration=time_t
                )
            case "f":  # F
                print("Flying direct: going down")
                mambo.fly_direct(
                    roll=0, pitch=0, yaw=0, vertical_movement=-10, duration=time_t
                )
            case "d":  # D
                print("Flying direct: going left")
                mambo.fly_direct(
                    roll=strengh, pitch=0, yaw=0, vertical_movement=0, duration=time_t
                )
            case "q":  # Q
                print("Flying direct: going right")
                mambo.fly_direct(
                    roll=-strengh, pitch=0, yaw=0, vertical_movement=0, duration=time_t
                )
            case "z":  # Z
                print("Flying direct: going forward")
                mambo.fly_direct(
                    roll=0, pitch=strengh, yaw=0, vertical_movement=0, duration=time_t
                )
            case "s":  # S
                print("Flying direct: going backward")
                mambo.fly_direct(
                    roll=0, pitch=-strengh, yaw=0, vertical_movement=0, duration=time_t
                )
            case "a":  # A
                print("Flying direct: turning left")
                mambo.turn_degrees(-10)
            case "e":  # E
                print("Flying direct: turning right")
                mambo.turn_degrees(10)
        print("flying state is %s" % mambo.sensors.flying_state)
        mambo.ask_for_state_update()


if __name__ == "__main__":
    root = tk.Tk()
    time_t = 0.1
    strengh = 20
    parr = Parrot(root)
    parr.pack(fill="both", expand=True)

    # you will need to change this to the address of YOUR mambo
    mamboAddr = "e0:14:d0:63:3d:d0"

    # make my mambo object
    # remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
    mambo = Mambo(mamboAddr, use_wifi=True)

    print("trying to connect")
    success = mambo.connect(num_retries=3)
    # success = True
    print("connected: %s" % success)
    if success:
        try:
            print("sleeping")
            mambo.ask_for_state_update()
            mambo.smart_sleep(2)

            parr.clock()
            root.mainloop()

        except KeyboardInterrupt:
            print("disconnect")
            mambo.safe_land(2)
            mambo.smart_sleep(2)
            mambo.disconnect()
