"""Module for controlling the drone through the radio control command"""

class DroneController:
    """Intermediary for sending rc commands to drone. This class keeps
track of the last command sent to the drone and only forwards on new
commands if they differ from the last one sent. This avoid sending the
same command every video frame to the drone.

input parameters are an instance of the Drone class in drone.py and
    the speed of movements (0-100)

    """
    def __init__(self, drone, speed=20):
        self.drone = drone
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0
        self.speed = int(speed)
        self.changed = False

    def set_up_down(self, direction):
        """Set the up_down direction if it differs from current status"""
        value = -self.speed * int(direction)
        if self.up_down != value:
            self.up_down = value
            self.changed = True

    def set_yaw(self, direction):
        """Set the yaw direction if it differs from current status"""
        value = self.speed * int(direction)
        if self.yaw != value:
            self.yaw = value
            self.changed = True

    def send(self):
        """Send the current state of controller to drone if it's been updated"""
        if self.changed:
            self.drone.rc(self.left_right, self.forward_backward, self.up_down, self.yaw)
        self.changed = False

    def stop(self):
        """Set drone controls to zero - stop moving"""
        if self.up_down != 0:
            self.up_down = 0
            self.changed = True

        if self.yaw != 0:
            self.yaw = 0
            self.changed = True

        self.send()