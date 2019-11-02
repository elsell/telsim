"""Finite state machine for automated drone flight"""
import time
import recognition

class State:
    def react(self, target):
        raise NotImplementedError("Override react in derived class")


class LookAround(State):
    """Rotate around until the drone sees the target"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.controller.stop()
        self.move()

        self.start_time = time.monotonic()
        print('LookAround:enter')

    def react(self, target):
        elapsed_time = time.monotonic() - self.start_time
        if elapsed_time > 5:
            print('LookAround: timeout')
            self.controller.stop()
            return None

        if target:
            print('LookAround: target found')
            return LookAt(self.identifier, self.controller)
        else:
            return self

    def move(self):
        self.controller.set_yaw(20)
        self.controller.send()

    
class LookAt(State):
    """Move drone up or down and rotate to center the target in view"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        print('LookAt: enter')
        
    def react(self, target):
        if recognition.target_centered(target.dx, target.dy):
            print('LookAt: target centered')
            return FlyTo(self.identifier, self.controller)
        else:
            self.move(target)
            return self

    def move(self, target):
        dx = target.dx
        dy = target.dy
        yaw = 0 if dx == 0 else int(dx/abs(dx))*20
        up_down = 0 if dy == 0 else int(dy/abs(dy))*-20
        self.controller.set_yaw(yaw)
        self.controller.set_up_down(up_down)
        self.controller.send()


class FlyTo(State):
    """Move drone towards or away from target"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        print('FlyTo: enter')

    def react(self, target):
        if not recognition.target_centered(target.dx, target.dy):
            print('FlyTo: target not centered')
            return LookAt(self.identifier, self.controller)
        else: # target centered
            return None
                
        
class Aligned(State):
    """Check if drone is in position"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        print('Aligned:enter')

    def react(self, target):
        if recognition.target_centered(target.dx, target.dy):
            print('Aligned: successfully aligned')
            self.controller.stop()
            return None
        else:
            print('Aligned: target not centered')
            return LookAt(self.identifier, self.controller)
    
        
# class FlyTo(State):
#     """Move drone towards or away from target based on distance"""
#     def __init__(self, identifier, controller):
#         self.identifier = identifier
#         self.controller = controller
#         print("FlyTo:enter")

#     def react(self, target):
        
        
class AlignmentFSM:
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.state = LookAround(identifier, controller)
        self.no_target_frame_count = 0
        self.no_target_frame_limit = 10

    def on_frame(self, frame):
        # should wait multiple frames where no target is found in case
        # those frames are corrupt or the lighting on the target isn't
        # good
        target = self.identifier.find_target(frame)
        if target:
            self.no_target_frame_count = 0 # reset counter
            self.state = self.state.react(target)
        else:
            self.no_target_frame_count += 1
            if self.no_target_frame_count > self.no_target_frame_limit:
                if not isinstance(self.state, LookAround):
                    self.state = LookAround(self.identifier, self.controller)
                self.state = self.state.react(None)
        return self.state
