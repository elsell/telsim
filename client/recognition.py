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
              'fuschia': ((156, 184, 30), (180, 255, 255)),
              'fuschia-webcam': ((138, 140, 30), (187, 255, 255)),
              'blue-webcam': ((110, 72, 34), (130, 255, 255)),
}

def threshold_image(image, color):
    # blur image, but keep edges
    blur = cv2.bilateralFilter(image, 11, 17, 17)

    # convert to HSV and threshold image
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv, *thresholds[color])

    # remove any small blobs
    thresh = cv2.erode(thresh, None, iterations=1)
    thresh = cv2.dilate(thresh, None, iterations=1)
    return thresh

def find_contour(thresh, minimum_area=400):
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[1]

    for c in sorted(contours, key=cv2.contourArea, reverse=True):
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.05*peri, True)
        area = cv2.contourArea(c)
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

def get_points(contour):
    return contour.ravel().reshape((4, 2))

def pairwise(iterable):
    """s -> (s0, s1), (s1, s2), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def draw_lines(image, points):
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 0)]
    for (p1, p2), c in zip(pairwise(points), colors):
        cv2.line(image, p1, p2, color, 2)

def get_centroid(contour):
    M = cv2.moments(contour)
    x = int(M["m10"] / M["m00"])
    y = int(M["m01"] / M["m00"])
    return x, y

def found_target(contour):
    return contour is not None

def image_center(image):
    height, width, _ = image.shape
    cx = width//2
    cy = height//2
    return cx, cy

def centroid_displacement(contour, image):
    cx, cy = image_center(image)
    x, y = get_centroid(contour)
    dx = x - cx
    dy = y - cy
    return dx, dy

def target_within_limits(displacement, delta = 20):
    dx, dy = displacement
    return dx**2 + dy**2 <= delta**2

def find_target(frame, target):
    thresh = threshold_image(frame, target)
    contour = find_contour(thresh)
    return contour

def calculate_direction(delta, eps=20):
    magnitude = abs(delta)
    if magnitude > eps:
        direction = int(delta / magnitude)
        return direction
    else:
        return 0



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
        contour_outer = find_target(frame, self.color_outer)
        contour_inner = find_target(frame, self.color_inner)
    
        if (found_target(contour_outer) and
            found_target(contour_inner) and
            contained_within(contour_outer, contour_inner)):
            # found target, so reset counter
            self.no_target_frame_count = 0

            # compute displacements and directions to move drone
            dx, dy = centroid_displacement(contour_outer, frame)
            cx, cy = image_center(frame)
            yaw = calculate_direction(dx)
            up_down = calculate_direction(dy)

            # send drone directions
            self.controller.set_yaw(yaw)
            self.controller.set_up_down(up_down)
            self.controller.send()

            if draw:
                # draw contours on frame
                cv2.line(frame, (cx, cy), (cx+dx, cy+dy), (0, 0, 255), 1)
                cv2.drawContours(frame, [contour_outer], -1, (0, 255, 0), 0)
                cv2.drawContours(frame, [contour_inner], -1, (0, 255, 0), 0)
                centroid = get_centroid(contour_outer)
                cv2.circle(frame, centroid, 3, (255, 255, 255), -1)

        else:
            self.no_target_frame_count += 1
            if self.no_target_frame_count > 10:
                self.controller.stop()
                no_target_frame_count = 0
