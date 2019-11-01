"""Finite state machine for automated drone flight"""
import time
import recognition

class State:
    def on_frame(self, frame):
        raise NotImplementedError("Override on_frame in derived class")


class LookAround(State):
    """Rotate around until the drone sees the target"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.controller.set_yaw(1)
        self.start_time = time.monotonic()
        print('LookAround:enter')

    def on_frame(self, frame):
        elapsed_time = time.monotonic() - self.start_time
        if elapsed_time > 5:
            print('LookAround:timeout')
            return None

        if self.identifier.find_contour(frame):
            print('LookAround:exit')
            return LookAt(self.identifier, self.controller)
        else:
            return self

    
class LookAt(State):
    """Move drone up or down and rotate to center the target in view"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        print('LookAt:enter')
        
    def on_frame(self, frame):
        if self.identifier.find_contour(frame):
            self.identifier.draw()
            dx, dy = self.identifier.displacement()
            yaw = recognition.direction(dx)
            up_down = recognition.direction(dy)
            self.controller.set_yaw(yaw)
            self.controller.set_up_down(up_down)
            self.controller.send()
            return self
        else:
            print('LookAt:exit')
            return LookAround(self.identifier, self.controller)


class AlignmentFSM:
    def __init__(self, identifier, controller):
        self.state = LookAround(identifier, controller)

    def on_frame(self, frame):
        self.state = self.state.on_frame(frame)
        return self.state
