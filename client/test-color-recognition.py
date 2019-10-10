import cv2
import drone
import controller

# colors to describe target
color_outer = 'fuschia-webcam'
color_inner = 'blue-webcam'

drone = drone.FakeDrone()
control = controller.DroneController(drone)
finder = controller.FindTarget(control, color_outer, color_inner)

drone.battery()
drone.takeoff()

while True:
    frame = drone.get_frame()
    finder.process(frame, draw=True)
        
    cv2.imshow('window', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1) & 0xFF == ord('p'):
        print('took picture')
        cv2.imwrite('test.jpg', frame)

drone.land()
cv2.destroyAllWindows()


