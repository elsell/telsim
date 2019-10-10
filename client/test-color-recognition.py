import cv2
import drone
import controller
import recognition as rec

drone = drone.FakeDrone()
control = controller.DroneController(drone)

color_outer = 'fuschia-webcam'
color_inner = 'blue-webcam'
no_target_frame_count = 0

drone.battery()
drone.takeoff()

while True:
    # get one video frame
    frame = drone.get_frame()

    # attempt to find two contours
    contour_outer = rec.find_target(frame, color_outer)
    contour_inner = rec.find_target(frame, color_inner)
    
    if (rec.found_target(contour_outer) and rec.found_target(contour_inner) and
        rec.contained_within(contour_outer, contour_inner)):

        no_target_frame_count = 0

        # compute displacements and directions to move drone
        dx, dy = rec.centroid_displacement(contour_outer, frame)
        cx, cy = rec.image_center(frame)
        yaw = rec.calculate_direction(dx)
        up_down = rec.calculate_direction(dy)

        # send drone directions
        control.set_yaw(yaw)
        control.set_up_down(up_down)
        control.send()

        # draw contours on frame
        cv2.line(frame, (cx, cy), (cx+dx, cy+dy), (0, 0, 255), 1)
        cv2.drawContours(frame, [contour_outer], -1, (0, 255, 0), 0)
        cv2.drawContours(frame, [contour_inner], -1, (0, 255, 0), 0)
        centroid = rec.get_centroid(contour_outer)
        cv2.circle(frame, centroid, 3, (255, 255, 255), -1)
        
    else:
        no_target_frame_count += 1
        if no_target_frame_count > 10:
            control.stop()
            no_target_frame_count = 0

    cv2.imshow('window', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1) & 0xFF == ord('p'):
        print('took picture')
        cv2.imwrite('test.jpg', frame)

drone.land()
cv2.destroyAllWindows()


