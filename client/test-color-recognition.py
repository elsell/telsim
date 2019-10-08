import cv2
import drone
import controller
import recognition as rec

drone = drone.FakeDrone()
control = controller.DroneController(drone)

color = 'fuschia-webcam'
no_target_frame_count = 0

drone.battery()
drone.takeoff()

while True:
    frame = drone.get_frame()
    contour = rec.find_target(frame, color)
    if rec.found_target(contour):
        no_target_frame_count = 0
        dx, dy = rec.centroid_displacement(contour, frame)
        cx, cy = rec.image_center(frame)
        cv2.line(frame, (cx, cy), (cx+dx, cy+dy), (0, 0, 255), 1)
        yaw = rec.calculate_direction(dx)
        control.set_yaw(yaw)
        up_down = rec.calculate_direction(dy)
        control.set_up_down(up_down)
        control.send()
        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 0)
        centroid = rec.get_centroid(contour)
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


