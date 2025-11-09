import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(1)


mpHands = mp.solutions.hands
hands = mpHands.Hands(True)


# displaying output from webcam
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frameRGB)
    # print(results.multi_hand_landmarks)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(id, cx, cy)
                if id == 4:
                    cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            mp.solutions.drawing_utils.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow('Webcam Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()