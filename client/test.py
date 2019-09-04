from drone import Drone

with Drone() as d:
    d.speed()
    d.battery()
    d.up(100)
    d.forward(100)
    d.back(100)
    d.ccw(360)
    
