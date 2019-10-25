"""Finite state machine for automated drone flight"""
import time
import recognition

class State:
    def on_frame(self, frame):
        raise NotImplementedError("Override on_frame in derived class")


class Seek(State):
    """Rotate around until the drone sees the target"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.controller.set_yaw(1)
        self.start_time = time.monotonic()

    def on_frame(self, frame):
        elapsed_time = time.monotonic() - self.start_time
        if elapsed_time > 5:
        contour = self.identifier.find_contour(frame)
        if contour is None:
            return self
        else:
            return LookAt(self.identifier, self.controller)

    
class LookAt(State):
    """Move drone up or down and rotate to center the target in view"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        
    def on_frame(self, frame):
        contour = self.identifier.find_contour(frame)
        if contour is not None:
            dx, dy = recognition.centroid_displacement(contour, frame)
            yaw = recognition.direction(dx)
            up_down = recognition.direction(dy)
            self.controller.set_yaw(yaw)
            self.controller.set_up_down(up_down)
            self.controller.send()

        return self

class Machine:
    def __init__(self, init_state):
        self.state = init_state

    def on_frame(self, frame):
        self.state = self.state.on_frame(frame)
