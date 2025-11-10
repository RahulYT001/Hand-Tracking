import cv2
import mediapipe as mp
import time



class handDetector:
    def __init__(self, mode = False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpHands = mp.solutions.hands
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, frame, draw = True):
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(frameRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(frame, handLms, self.mpHands.HAND_CONNECTIONS)
        return frame

    def findPosition(self, frame, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lmList



def main():
    cap = cv2.VideoCapture(1)
    # FPS calculation variables
    pTime = 0
    cTime = 0
    detector = handDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Use the detector class to find hands
        frame = detector.findHands(frame)

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

if __name__ == "__main__":
    main()