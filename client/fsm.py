"""Finite state machine for automated drone flight"""
import time
import recognition

# The alignment procedure will stop if a target is not seen for many
# frames or a timeout is reached
no_target_frame_count = 10
timeout = 10


# Parameters to adjust when target alignment goals are met
radius_centered = 50
distance_min = 0.8
distance_max = 1.0
ratio_min = 0.95
ratio_max = 1.05


# Functions that determine if goals are met
def target_centered(dx, dy):
    """Calculates whether the target is centered in the drone's view"""
    return dx**2 + dy**2 <= radius_centered**2

def good_distance(distance):
    """Calculates if the distance to target is within range"""
    return distance_min < distance < distance_max

def good_left_right(ratio):
    """Calculates if the drone is perpendicular enough to the target"""
    return ratio_min < ratio < ratio_max



# Below is the finite state machine code.

# AlignmentFSM is the main interface to a finite state machine that
# recognizes a target and directs the drone to fly towards it,
# ultimately positioning itself within the constraints specified
# above.

# The internal state of the finite state machines changes depending on
# the values of the target data. Each state is given a controller
# object (to control the drone) and must implement the class method
# react() which takes an instance of recognition.TargetData as its
# argument. React() must return self or a new State.

class State:
    """Base class for all states in the FSM"""
    def react(self, target):
        """Method to overload. Takes in a recognition.TargetData object and
must return a State object (either self or a new State)."""
        raise NotImplementedError("Override react in derived class")


class LookAround(State):
    """Rotate around until the drone sees the target"""
    def __init__(self, controller):
        self.controller = controller
        self.controller.stop()
        self.move()

        self.start_time = time.monotonic()
        print('LookAround: enter')

    def react(self, target):
        """Check if the timeout has been reached (terminate the FSM by
returning None) or transition to LookAt"""
        elapsed_time = time.monotonic() - self.start_time
        if elapsed_time > timeout:
            print('LookAround: timeout')
            self.controller.stop()
            return None

        if target:
            print('LookAround: target found')
            return LookAt(self.controller)
        else:
            return self

    def move(self):
        self.controller.set_yaw(40)
        self.controller.send()

    
class LookAt(State):
    """Move drone up or down and rotate to center the target in view"""
    def __init__(self, controller):
        self.controller = controller
        self.controller.stop()
        print('LookAt: enter')
        
    def react(self, target):
        """Transition to FlyTo if target is centered, otherwise move"""
        if target_centered(target.dx, target.dy):
            print('LookAt: target centered')
            return FlyTo(self.controller)
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
    def __init__(self, controller):
        self.controller = controller
        self.controller.stop()
        print('FlyTo: enter')

    def react(self, target):
        """If target is not centered transition to LookAt, if the distance is
good transition to Strafe, otherwise move"""
        if not target_centered(target.dx, target.dy):
            print('FlyTo: target not centered')
            return LookAt(self.controller)

        if good_distance(target.distance):
            return Strafe(self.controller)
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
    def __init__(self, controller):
        self.controller = controller
        self.controller.stop()
        print('Strafe: enter')

    def react(self, target):
        """Strafe is the final state before checking if alignment
succeeds. Therefore, check each criterion and transition to the
appropriate state if not met. If all criterion are met transition to
Aligned state, otherwise move.

        """
        if not target_centered(target.dx, target.dy):
            print('Strafe: target not centered')
            return LookAt(self.controller)
        elif not good_distance(target.distance):
            print('Strafe: target distance wrong')
            return FlyTo(self.controller)
        elif good_left_right(target.ratio):
            return Aligned(self.controller)
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
    def __init__(self, controller):
        self.controller = controller
        self.controller.stop()
        print('Aligned:enter')

    def react(self, target):
        """Final verification of drone alignment. If aligned return None to
terminate FSM, otherwise transition to LookAt."""
        if (target_centered(target.dx, target.dy) and
            good_distance(target.distance) and
            good_left_right(target.ratio)):
            print('Aligned: successfully aligned')
            self.controller.stop()
            return None
        else:
            print('Aligned: target not centered')
            return LookAt(self.controller)
    
        
class AlignmentFSM:
    """AlignmentFSM operates like this:
1) The method on_frame() receives a video frame.
2) It then uses recognition.TargetIdentifier to attempt to recognize a target
   within its view.
3) If a target is found it passes a instance of recognition.TargetData to
   its internal state's react() method.
4) Otherwise it waits some number of frames, then changes to LookAround.

It returns its internal state to every call of on_frame. The
terminating condition is that its internal state will eventually be
None.

    """
    def __init__(self, identifier, controller):
        self.identifier = identifier # used to find target
        self.controller = controller # used to control drone

        # start by looking around for the target
        self.state = LookAround(controller)

        # keep track of number of frame where no target is found
        self.no_target_frame_count = 0
        self.no_target_frame_limit = no_target_frame_count

    def on_frame(self, frame):
        """Modify the internal state based on the video frame"""
        target = self.identifier.find_target(frame)

        if target: # target is found
            self.no_target_frame_count = 0 # reset counter
            self.state = self.state.react(target) # pass target data to interal state
        else:
            # We should wait multiple frames when no target is found
            # and not quit immediately.  This is in case those frames
            # are corrupt or the lighting on the target isn't good.
            self.no_target_frame_count += 1
            if self.no_target_frame_count > self.no_target_frame_limit:
                if not isinstance(self.state, LookAround):
                    # maybe the target is blocked from view, we should
                    # try looking around
                    self.state = LookAround(self.controller)
                self.state = self.state.react(None)

        return self.state
