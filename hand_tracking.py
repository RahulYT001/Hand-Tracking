import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(1)

# FPS calculation variables
pTime = 0
cTime = 0

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

    # Calculate and display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    # Aesthetic FPS display with background
    fps_text = f'FPS: {int(fps)}'
    text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    
    # Create a rounded rectangle background
    cv2.rectangle(frame, (10, 10), (text_size[0] + 30, 50), (0, 0, 0), -1)  # Black background
    cv2.rectangle(frame, (10, 10), (text_size[0] + 30, 50), (0, 255, 0), 2)  # Green border
    
    # Display FPS text in white
    cv2.putText(frame, fps_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow('Webcam Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()