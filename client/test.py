from drone import Drone, WebcamDrone

with Drone() as d:
    d.battery()
    d.takeoff()
    d.align_to_target()


