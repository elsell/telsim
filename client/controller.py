"""Module for controlling the drone through the radio control command"""
import cv2


class DroneController:
    """Intermediary for sending rc commands to drone. This class keeps
track of the last command sent to the drone and only forwards on new
commands if they differ from the last one sent. This avoid sending the
same command every video frame to the drone.

input parameters are an instance of the Drone class in drone.py

    """
    def __init__(self, drone):
        self.drone = drone
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0
        self.changed = False

    def set_left_right(self, value):
        """Set the left_right direction if it differs from the current status"""
        if self.left_right != value:
            self.left_right = value
            self.changed = True

    def set_forward_backward(self, value):
        """Set the forward_backward direction if it differs from the current status"""
        if self.forward_backward != value:
            self.forward_backward = value
            self.changed = True
        
    def set_up_down(self, value):
        """Set the up_down direction if it differs from the current status"""
        if self.up_down != value:
            self.up_down = value
            self.changed = True

    def set_yaw(self, value):
        """Set the yaw direction if it differs from the current status"""
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
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0
        self.changed = True

        self.send()

