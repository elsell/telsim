"""Finite state machine for automated drone flight"""
import time
import recognition

dropped_frame_count = 10
timeout = 10
radius_centered = 50
distance_min = 0.8
distance_max = 1.0
ratio_min = 0.95
ratio_max = 1.05

def target_centered(dx, dy):
    return dx**2 + dy**2 <= radius_centered**2

def good_distance(distance):
    return distance_min < distance < distance_max

def good_left_right(ratio):
    return ratio_min < ratio < ratio_max

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
        print('LookAround: enter')

    def react(self, target):
        elapsed_time = time.monotonic() - self.start_time
        if elapsed_time > timeout:
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
        self.controller.stop()
        print('LookAt: enter')
        
    def react(self, target):
        if target_centered(target.dx, target.dy):
            print('LookAt: target centered')
            return FlyTo(self.identifier, self.controller)
        else:
            self.move(target)
            return self

    def move(self, target):
        dx = target.dx
        dy = target.dy
        yaw = 0 if dx == 0 else int(dx/abs(dx))*10
        up_down = 0 if dy == 0 else int(dy/abs(dy))*10
        self.controller.set_yaw(yaw)
        self.controller.set_up_down(up_down)
        self.controller.send()


class FlyTo(State):
    """Move drone towards or away from target"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.controller.stop()
        print('FlyTo: enter')

    def react(self, target):
        if not target_centered(target.dx, target.dy):
            print('FlyTo: target not centered')
            return LookAt(self.identifier, self.controller)

        if good_distance(target.distance):
            return Strafe(self.identifier, self.controller)
        else:
            self.move(target)
            return self

    def move(self, target):
        value = 0
        if target.distance > distance_max:
            value = 10
        if target.distance < distance_min:
            value = -10

        self.controller.set_forward_backward(value)
        self.controller.send()
        

class Strafe(State):
    """Move drone left/right to be in front of target"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.controller.stop()
        print('Strafe: enter')

    def react(self, target):
        if not target_centered(target.dx, target.dy):
            print('Strafe: target not centered')
            return LookAt(self.identifier, self.controller)
        elif not good_distance(target.distance):
            print('Strafe: target distance wrong')
            return FlyTo(self.identifier, self.controller)
        elif good_left_right(target.ratio):
            return Aligned(self.identifier, self.controller)
        else: # bad left/right
            self.move(target)
            return self

    def move(self, target):
        value = 0
        if target.ratio < ratio_min:
            value = -20
        if target.ratio > ratio_max:
            value = 20

        self.controller.set_left_right(value)
        self.controller.send()
            
            
        
        
class Aligned(State):
    """Check if drone is in position"""
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.controller.stop()
        print('Aligned:enter')

    def react(self, target):
        if (target_centered(target.dx, target.dy) and
            good_distance(target.distance) and
            good_left_right(target.ratio)):
            print('Aligned: successfully aligned')
            self.controller.stop()
            return None
        else:
            print('Aligned: target not centered')
            return LookAt(self.identifier, self.controller)
    
        
class AlignmentFSM:
    def __init__(self, identifier, controller):
        self.identifier = identifier
        self.controller = controller
        self.state = LookAround(identifier, controller)
        self.no_target_frame_count = 0
        self.no_target_frame_limit = dropped_frame_count

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
