import numpy as np
import cv2
import matplotlib.pyplot as plt
print(cv2.__version__)
target = cv2.imread("target.png")
#target = cv2.imread("pattern.png")
target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

detector = cv2.ORB_create(scoreType=cv2.ORB_FAST_SCORE)
#detector = cv2.ORB_create()
target_kp, target_des = detector.detectAndCompute(target, None)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_kp, frame_des = detector.detectAndCompute(frame, None)
    
    # find matches
    matches = bf.match(target_des, frame_des)
    
    # sort them in order of distance
    matches = sorted(matches, key=lambda x: x.distance)

    good_matches = matches[:10]
    src_pts = np.float32([target_kp[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
    dst_pts = np.float32([frame_kp[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()
    h, w = target.shape[:2]
    pts = np.float32([[0,0], [0,h-1], [w-1,h-1], [w-1,0]]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M)
    dst += (w, 0)
    draw_params = dict(matchColor = (0,255,0),
                       singlePointColor = None,
                       matchesMask = matchesMask,
                       flags = 2)
    frame = cv2.drawMatches(target, target_kp, frame, frame_kp, good_matches,
                            outImg=frame, **draw_params)
    frame = cv2.polylines(frame, [np.int32(dst)], True, (0,0,255), 3, cv2.LINE_AA)
    
    cv2.imshow('window', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()

