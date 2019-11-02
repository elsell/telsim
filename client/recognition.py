"""Module for processing the video stream from the drone and reacting
to objects within it"""
import cv2

# HSV thresholds for colors used in testing
thresholds = {'green': ((15, 193, 128), (39, 244, 207)),
              'green2': ((27, 123, 37), (38, 227, 255)),
              'red': ((0, 151, 0), (7, 255, 255)),
              'purple': ((139, 69, 0), (161, 255, 255)),
              'purple2': ((121, 53, 11), (165, 255, 255)),
              'blue': ((38, 145, 64), (156, 255, 255)),
              'teal': ((97, 60, 49), (103, 255, 255)),
              'teal-webcam': ((95, 186, 118), (147, 255, 255)),
              'fuschia': ((118, 129, 37), (177, 255, 255)),
              'blue': ((106, 94, 44), (138, 255, 255)),
              'fuschia-webcam': ((138, 140, 30), (187, 255, 255)),
              'blue-webcam': ((110, 72, 34), (130, 255, 255)),
}

def threshold_image(image, color):
    """Select only the objects in the image that match the given color"""
    # blur image, reduce noise, keep edges
    blur = cv2.bilateralFilter(image, 11, 17, 17)

    # convert to HSV and threshold image
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv, *thresholds[color])

    # remove any small blobs
    thresh = cv2.erode(thresh, None, iterations=1)
    thresh = cv2.dilate(thresh, None, iterations=1)
    return thresh

def find_square(image, minimum_area=400):
    """Attempt to find a 4-sided polygon in the image with a minimum
area. Return it if successful otherwise return None.

    """
    # find all possible contours in image
    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[1]

    # sort the contours by area, largest to smallest
    for c in sorted(contours, key=cv2.contourArea, reverse=True):
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.05*peri, True)
        area = cv2.contourArea(c)
        # select polygons that are 4-sided and greater than minimum area
        if len(approx) == 4 and area >= minimum_area:
            return approx

    return None

def contained_within(contour_larger, contour_smaller):
    """Test if contour_smaller is contained within contour_larger"""
    for (x,y) in contour_smaller[0]:
        result = cv2.pointPolygonTest(contour_larger, (x,y), False)
        if result != 1:
            return False
    return True

def sorted_points(contour):
    """Extract points from a 4-point contour"""
    points = contour.ravel().reshape((4, 2))
    a, b, c, d = [(x, y) for (x, y) in sorted(points, key=lambda xy: xy[0])]
    if a[1] > b[1]:
        a, b = b, a
    if c[1] > d[1]:
        c, d = d, c
    return a, b, c, d

def vertical_line_lengths(contour):
    a, b, c, d = sorted_points(contour)
    left = b[1] - a[1]
    right = d[1] - c[1]
    return left, right

def vertical_line_ratio(contour):
    left, right = vertical_line_lengths(contour)
    return left / right

def distance(contour):
    left, right = vertical_line_lengths(contour)
    avg = (left + right) / 2
    factor = 88.7 # webcam
    return factor / avg # meters

def centroid(contour):
    """Return the centroid of the contour"""
    M = cv2.moments(contour)
    x = int(M["m10"] / M["m00"])
    y = int(M["m01"] / M["m00"])
    return x, y

def image_center(image):
    """Calculate the center pixel of the image and return (x, y)"""
    height, width, _ = image.shape
    cx = width//2
    cy = height//2
    return cx, cy

def centroid_displacement(contour, image):
    """Calculate the displacement between the contour's centroid and the image center"""
    cx, cy = image_center(image)
    x, y = centroid(contour)
    dx = x - cx
    dy = cy - y # assume positive dy means move drone up
    return dx, dy

def target_centered(dx, dy, radius=20):
    """Determine if the target is centered within the given pixel
radius"""
    return dx**2 + dy**2 <= radius**2

def find_square_contour(frame, color):
    """Find a colored square target within the frame and return the enclosing contour"""
    thresh = threshold_image(frame, color)
    contour = find_square(thresh)
    return contour

def direction(delta, eps=20):
    """Given a centroid displacement value, calculate the direction to move"""
    magnitude = abs(delta)
    if magnitude > eps:
        direction = int(delta / magnitude)
        return direction
    else:
        return 0
    

class TargetData:
    def __init__(self, contour, dx, dy, distance, ratio):
        self.contour = contour
        self.dx = dx
        self.dy = dy
        self.distance = distance
        self.ratio = ratio
    
class TargetIdentifier:
    def __init__(self, color_outer, color_inner):
        self.color_outer = color_outer
        self.color_inner = color_inner

    def find_target(self, frame):
        contour_outer = find_square_contour(frame, self.color_outer)
        contour_inner = find_square_contour(frame, self.color_inner)
        if (contour_outer is not None and
            contour_inner is not None and
            contained_within(contour_outer, contour_inner)):
            dx, dy = centroid_displacement(contour_outer, frame)
            dist = distance(contour_outer)
            ratio = vertical_line_ratio(contour_outer)
            target_data = TargetData(contour_outer, dx, dy, dist, ratio)
            self.draw(frame, target_data)
            return target_data
        else:
            return None

    def draw(self, frame, target_data):
        cv2.drawContours(frame, [target_data.contour], -1, (0, 255, 0), 0)
        cv2.putText(frame, "dx: {:+4d}".format(target_data.dx), (10, 250),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, "dy: {:+4d}".format(target_data.dy), (10, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, "dist: {:+4.2f}".format(target_data.distance), (10, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, "ratio: {:+1.3f}".format(target_data.ratio), (10, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 1, cv2.LINE_AA)
        

class FindTarget:
    def __init__(self, controller, identifier):
        self.controller = controller
        self.identifier = identifier
        self.no_target_frame_count = 0

    def process(self, frame, draw=False):
        if self.identifier.find_contour(frame):
            # found target, so reset counter
            self.no_target_frame_count = 0

            # adjust drone to look at target
            dx, dy = self.identifier.displacement()
            yaw = direction(dx)
            up_down = direction(dy)

            # compute distance and move drone towards target
            dist = self.identifier.distance()
            if dist > 0.55: # meters
                forward_backward = 1
            elif dist < 0.45:
                forward_backward = -1
            else:
                forward_backward = 0

            # compute left-right based on ratio of sides of target
            ratio = self.identifier.vertical_line_ratio()
            if ratio < 0.95:
                left_right = -1
            elif ratio > 1.05:
                left_right = 1
            else:
                left_right = 0
                
            # send drone directions
            self.controller.set_left_right(left_right)
            self.controller.set_forward_backward(forward_backward)
            self.controller.set_yaw(yaw)
            self.controller.set_up_down(up_down)
            self.controller.send()

            if draw:
                # draw contours on frame
                #cv2.line(frame, (cx, cy), (cx+dx, cy+dy), (0, 0, 255), 1)
                contour = self.identifier.contour_outer
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 0)
                #cent = centroid(contour)
                #cv2.circle(frame, cent, 3, (255, 255, 255), -1)

        else:
            self.no_target_frame_count += 1
            if self.no_target_frame_count > 10:
                self.controller.stop()
                no_target_frame_count = 0
