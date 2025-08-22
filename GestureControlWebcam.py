import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import mediapipe as mp
import serial
import time

esp32 = serial.Serial('COM8', 115200, timeout=1)
time.sleep(2)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

last_left_buzz = -1  # Left hand controls buzzer
last_led_cmd = ""    # To avoid re-sending same LED command

def finger_states(hand_landmarks, label):
    tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    states = []
    
    # ---- Thumb (orientation adjusted) ----
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[2]
    
    if label == "Left":
        states.append(1 if thumb_tip.x > thumb_ip.x else 0)
    else:
        states.append(1 if thumb_tip.x < thumb_ip.x else 0)
    
    # ---- Other fingers ----
    for tip in tips[1:]:
        pip = hand_landmarks.landmark[tip - 2]
        if hand_landmarks.landmark[tip].y < pip.y:
            states.append(1)  # finger extended
        else:
            states.append(0)  # finger curled
    
    return states

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    leds_text = ""
    buzzer_text = ""

    if results.multi_hand_landmarks and results.multi_handedness:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            label = results.multi_handedness[i].classification[0].label
            states = finger_states(hand_landmarks, label)
            finger_count = sum(states)

            # Right hand → LEDs
            if label == "Right":
                cmd = "L" + "".join(str(s) for s in states) + "\n"
                if cmd != last_led_cmd:  # Only send if different
                    esp32.write(cmd.encode())
                    last_led_cmd = cmd
                leds_text = f"LEDs: {finger_count}"

            # Left hand → Buzzer
            elif label == "Left":
                buzz_state = 1 if finger_count > 2 else 0
                if buzz_state != last_left_buzz:  # Only send when state changes
                    esp32.write(f"B{buzz_state}\n".encode())
                    last_left_buzz = buzz_state
                buzzer_text = f"Buzzer: {'ON' if buzz_state else 'OFF'}"

    # Show texts (both can appear together)
    if leds_text:
        cv2.putText(frame, leds_text, (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if buzzer_text:
        cv2.putText(frame, buzzer_text, (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
