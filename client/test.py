from drone import Drone

with Drone(which='planner') as d:
    d.battery()
    d.takeoff()

    for i in range(8):
        d.go(0, 100, 10)
        d.cw(135)
