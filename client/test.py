from drone import Drone

with Drone(which='webcam') as d:
    d.battery()
    d.takeoff()
    d.align_to_target()


