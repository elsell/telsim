from drone import Drone

with Drone() as d:
    d.battery()
    d.takeoff()
    d.down(20)
    d.go(500, 0, 0)
    d.cw(180)
    d.go(500, 0, 0)
    d.cw(180)


