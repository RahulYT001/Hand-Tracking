import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(1)


mpHands = mp.solutions.hands
hands = mpHands.Hands(True)
mpDraw = mp.solutions.drawing_utils

# Drawing specifications for thin lines
drawSpec = mpDraw.DrawingSpec(thickness=0, circle_radius=2)
connectionSpec = mpDraw.DrawingSpec(thickness=1, color=(0, 255, 0))  # Green connections


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
                cx, cy = int(lm.x * w), int(lm.y * h) #actual pixel values
                print(id, cx, cy)
                if id == 4: #thumb tip
                    cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS, 
                                drawSpec, connectionSpec)

    cv2.imshow('Webcam Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()