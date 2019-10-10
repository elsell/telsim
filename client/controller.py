"""Module for controlling the drone through the radio control command"""
import cv2
import recognition

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



class FindTarget:
    def __init__(self, controller, color_outer, color_inner):
        self.controller = controller
        self.color_outer = color_outer
        self.color_inner = color_inner
        self.no_target_frame_count = 0
        self.contour_outer = None
        self.contour_inner = None

    def process(self, frame, draw=False):
        # attempt to find two contours
        contour_outer = recognition.find_target(frame, self.color_outer)
        contour_inner = recognition.find_target(frame, self.color_inner)
    
        if (recognition.found_target(contour_outer) and
            recognition.found_target(contour_inner) and
            recognition.contained_within(contour_outer, contour_inner)):
            # found target, so reset counter
            self.no_target_frame_count = 0

            # compute displacements and directions to move drone
            dx, dy = recognition.centroid_displacement(contour_outer, frame)
            cx, cy = recognition.image_center(frame)
            yaw = recognition.calculate_direction(dx)
            up_down = recognition.calculate_direction(dy)

            # send drone directions
            self.controller.set_yaw(yaw)
            self.controller.set_up_down(up_down)
            self.controller.send()

            if draw:
                # draw contours on frame
                cv2.line(frame, (cx, cy), (cx+dx, cy+dy), (0, 0, 255), 1)
                cv2.drawContours(frame, [contour_outer], -1, (0, 255, 0), 0)
                cv2.drawContours(frame, [contour_inner], -1, (0, 255, 0), 0)
                centroid = recognition.get_centroid(contour_outer)
                cv2.circle(frame, centroid, 3, (255, 255, 255), -1)

        else:
            self.no_target_frame_count += 1
            if self.no_target_frame_count > 10:
                self.controller.stop()
                no_target_frame_count = 0
