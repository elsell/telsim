import cv2
import drone
import controller
import recognition
import fsm

# colors to describe target
color_outer = 'fuschia' # 'fuschia-webcam'
color_inner = 'blue' # 'blue-webcam'

drone = drone.WebcamDrone()
#drone = drone.Drone()
control = controller.DroneController(drone)
identifier = recognition.TargetIdentifier(color_outer, color_inner)
finder = recognition.FindTarget(control, identifier)
aligner = fsm.AlignmentFSM(identifier, control)

drone.battery()
drone.takeoff()

while True:
    frame = drone.get_frame()

    if aligner.on_frame(frame) is None:
        # succeeded in alignment
        break

    cv2.imshow('window', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1) & 0xFF == ord('p'):
        print('took picture')
        cv2.imwrite('test.jpg', frame)

drone.land()
cv2.destroyAllWindows()


