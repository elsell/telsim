import cv2
import drone
import controller
import recognition

# colors to describe target
color_outer = 'fuschia' # 'fuschia-webcam'
color_inner = 'blue' # 'blue-webcam'
identifier = recognition.TargetIdentifier(color_outer, color_inner)

#drone = drone.WebcamDrone()
drone = drone.Drone()

drone.battery()

while True:
    frame = drone.get_frame()
    identifier.find_target(frame)

    cv2.imshow('window', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

drone.land()
cv2.destroyAllWindows()


