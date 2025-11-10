import cv2
import time
import numpy as np
import math
import subprocess
from hand_tracking_module import handDetector

# Function to control volume using nircmd (simpler approach)
def get_system_volume():
    try:
        # Get current system volume using PowerShell
        result = subprocess.run(['powershell', '-c', 
                               'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SystemInformation]::PowerStatus; (New-Object -ComObject WScript.Shell).SendKeys([char]0); Add-Type -TypeDefinition "using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\\"user32.dll\\")] public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam); }"; $vol = [Math]::Round([Audio]::Volume * 100); Write-Output $vol'],
                              capture_output=True, text=True, timeout=2)
        if result.stdout.strip():
            return int(result.stdout.strip())
    except:
        pass
    
    # Alternative method using wmic
    try:
        result = subprocess.run(['powershell', '-c', 
                               '(Get-AudioDevice -PlaybackVolume).Volume'],
                              capture_output=True, text=True, timeout=2)
        if result.stdout.strip():
            return int(float(result.stdout.strip()))
    except:
        pass
    
    # If all methods fail, return current estimated value
    return None

def set_volume(volume_level):
    try:
        # Use Windows command to set volume (0-100)
        volume_level = max(0, min(100, volume_level))  # Clamp between 0-100
        subprocess.run(['powershell', '-c', f'[audio]::Volume = {volume_level/100}'], 
                      capture_output=True)
    except:
        pass  # Continue if volume control fails

def increase_volume():
    try:
        subprocess.run(['powershell', '-c', 
                       '(New-Object -comObject Wscript.Shell).SendKeys([char]175)'],
                      capture_output=True)
    except:
        pass

def decrease_volume():
    try:
        subprocess.run(['powershell', '-c', 
                       '(New-Object -comObject Wscript.Shell).SendKeys([char]174)'],
                      capture_output=True)
    except:
        pass

# Initialize camera and detector
cap = cv2.VideoCapture(1)
detector = handDetector(detectionCon=0.7)

# Variables
pTime = 0
# Get actual system volume at startup
system_vol = get_system_volume()
volPer = system_vol if system_vol is not None else 50  # Use system volume or default to 50%
volBar = np.interp(volPer, [0, 100], [400, 150])  # Set bar position based on actual volume
last_gesture_time = 0
gesture_delay = 0.3  # Delay between volume changes
volume_sync_time = 0
volume_sync_interval = 2.0  # Sync with system volume every 2 seconds

print(f"Starting with system volume: {volPer}%")

while True:
    success, img = cap.read()
    
    # Find hands
    img = detector.findHands(img)
    
    # Get hand landmarks
    lmList = detector.findPosition(img, draw=False)
    
    current_time = time.time()
    
    # Periodically sync with actual system volume
    if current_time - volume_sync_time > volume_sync_interval:
        system_vol = get_system_volume()
        if system_vol is not None:
            volPer = system_vol
            volBar = np.interp(volPer, [0, 100], [400, 150])
        volume_sync_time = current_time
    
    if len(lmList) != 0:
        # Get thumb tip and thumb IP (interphalangeal joint)
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
        x2, y2 = lmList[3][1], lmList[3][2]  # Thumb IP joint
        
        # Get wrist position for reference
        x3, y3 = lmList[0][1], lmList[0][2]  # Wrist
        
        # Calculate thumb direction (up or down)
        thumb_direction = y1 - y3  # Negative means thumb is up
        
        # Draw points and line
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        
        # Calculate distance between thumb tip and IP joint
        length = math.hypot(x2 - x1, y2 - y1)
        
        # Control volume with delay to prevent rapid changes
        if current_time - last_gesture_time > gesture_delay:
            if thumb_direction < -50:  # Thumb up
                # Increase volume
                volPer = min(100, volPer + 5)  # Increase by 5%
                volBar = np.interp(volPer, [0, 100], [400, 150])
                
                # Send volume up command
                increase_volume()
                last_gesture_time = current_time
                
                # Visual feedback
                cv2.putText(img, "THUMB UP - VOLUME UP", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                
            elif thumb_direction > 50:  # Thumb down
                # Decrease volume
                volPer = max(0, volPer - 5)  # Decrease by 5%
                volBar = np.interp(volPer, [0, 100], [400, 150])
                
                # Send volume down command
                decrease_volume()
                last_gesture_time = current_time
                
                # Visual feedback
                cv2.putText(img, "THUMB DOWN - VOLUME DOWN", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else:
                # Neutral position
                cv2.putText(img, "NEUTRAL - NO CHANGE", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
        else:
            # Show current gesture but don't change volume
            if thumb_direction < -50:
                cv2.putText(img, "THUMB UP - COOLDOWN", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 255, 128), 3)
            elif thumb_direction > 50:
                cv2.putText(img, "THUMB DOWN - COOLDOWN", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 255), 3)
    
    # Draw volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    
    # Calculate and display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    # Aesthetic FPS display
    fps_text = f'FPS: {int(fps)}'
    text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    cv2.rectangle(img, (10, 10), (text_size[0] + 30, 50), (0, 0, 0), -1)
    cv2.rectangle(img, (10, 10), (text_size[0] + 30, 50), (0, 255, 0), 2)
    cv2.putText(img, fps_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow('Volume Control', img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

