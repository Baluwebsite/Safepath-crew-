
import cv2
import time
import numpy as np
import winsound
import threading
import datetime
import os
import math

# -------------------- CONFIGURATION FOR DRIVER SAFETY --------------------
# --- **NEW, STRICTER** Two-Factor Liveness (Blink + Motion) ---
# 1. Blink Detection:
LIVENESS_TIMEOUT_SECS = 5.0
BLINK_MIN_FRAMES = 3         # Increased to 3 for stricter detection
BLINK_MAX_FRAMES = 8         # Increased slightly to compensate
# 2. Motion Detection:
LIVENESS_NO_MOVEMENT_SECS = 4.0 # Increased timeout
STATIC_MOVEMENT_THRESHOLD_PIXELS = 4 # Increased to 4 to ignore camera jitter

# --- Other Alert Parameters ---
FACE_ABSENT_SECS = 5.0
BLOCKED_CONFIDENCE = 50.0 
ALERT_REPEAT_SECS = 5.0 

# --- Detection Parameters ---
EYE_SCALE_FACTOR = 1.1
EYE_MIN_NEIGHBORS = 5 
EYE_MIN_SIZE = (20, 20)

# --- Built-in Synthesized Sounds ---
SOUND_BLOCKED_STYLE = 'beep'
SOUND_BLOCKED_FREQ, SOUND_BLOCKED_DUR = 500, 2200
SOUND_NO_FACE_STYLE = 'siren'
SOUND_NO_FACE_FREQ, SOUND_NO_FACE_DUR = 1500, 2200
SOUND_STATIC_STYLE = 'buzzer'
SOUND_STATIC_FREQ, SOUND_STATIC_DUR = 2500, 2000

# --- File Paths & Window Title ---
LOG_FILE_PATH = "driver_monitoring_log.txt"
WINDOW_TITLE = "Driver Safety Monitor (Strict Liveness)"
# -------------------------------------------------------------------------

alert_active_event = threading.Event()

def play_alert_sound(frequency, duration_ms, alert_event, style='beep'):
    # This function remains the same as before
    def sound_thread():
        if not alert_event.is_set(): return
        if style == 'beep':
            end_time = time.time() + duration_ms / 1000.0; pulse_dur_ms = 50
            while time.time() < end_time:
                if not alert_event.is_set(): break
                winsound.Beep(frequency, pulse_dur_ms)
        elif style == 'buzzer':
            pulse_dur_ms = 40; pause_dur_s = 0.02; end_time = time.time() + duration_ms / 1000.0
            while time.time() < end_time:
                if not alert_event.is_set(): break
                winsound.Beep(frequency, pulse_dur_ms)
                time.sleep(pause_dur_s)
        elif style == 'siren':
            high_tone_freq = frequency; low_tone_freq = int(frequency * 0.7); tone_duration_ms = 180
            end_time = time.time() + duration_ms / 1000.0
            while time.time() < end_time:
                if not alert_event.is_set(): break
                winsound.Beep(high_tone_freq, tone_duration_ms)
                if not alert_event.is_set(): break
                winsound.Beep(low_tone_freq, tone_duration_ms)
    threading.Thread(target=sound_thread, daemon=True).start()

def log_event(message):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"{ts} (IST) | {message}"
    with open(LOG_FILE_PATH, "a") as f:
        f.write(full_message + "\n")
    print(f"\nLOG: {full_message}")

def get_image_variance(gray_frame):
    return cv2.Laplacian(gray_frame, cv2.CV_64F).var()

def main():
    cascades_path = cv2.data.haarcascades
    face_cascade_path = os.path.join(cascades_path, "haarcascade_frontalface_default.xml")
    eye_cascade_path = os.path.join(cascades_path, "haarcascade_eye.xml")
    if not os.path.exists(face_cascade_path) or not os.path.exists(eye_cascade_path):
        print("[FATAL ERROR] Could not find Haar Cascade files."); return
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    print("[INFO] Haar Cascade classifiers loaded successfully.")
    print(f"[INFO] Starting Driver Safety System from Vijayawada, Andhra Pradesh at {datetime.datetime.now().strftime('%I:%M:%S %p %Z')}...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    time.sleep(2.0)

    # --- State Variables ---
    last_alert_time = 0; last_known_face_time = time.time(); no_eyes_counter = 0
    # Liveness state variables
    last_blink_time = time.time()
    last_movement_time = time.time()
    last_face_center = None
    # Timestamps for persistent on-screen alerts
    block_start_time, no_face_start_time, static_image_start_time = None, None, None

    while True:
        ret, frame = cap.read()
        if not ret: continue
        frame = cv2.resize(frame, (600, 450)); gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY); now = time.time()
        status_text, color = "Initializing...", (255, 255, 0)
        
        variance = get_image_variance(gray)
        blocked = variance < BLOCKED_CONFIDENCE
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        num_faces = len(faces)
        
        if blocked:
            no_face_start_time, static_image_start_time = None, None; last_face_center = None
            if block_start_time is None: block_start_time = datetime.datetime.now()
            ts_str = block_start_time.strftime("%H:%M:%S")
            status_text, color = f"ALERT: CAMERA BLOCKED since {ts_str}", (0, 0, 255)
            
            if now - last_alert_time > ALERT_REPEAT_SECS:
                alert_active_event.set()
                play_alert_sound(SOUND_BLOCKED_FREQ, SOUND_BLOCKED_DUR, alert_active_event, style=SOUND_BLOCKED_STYLE)
                log_event(f"Camera Blocked Alert (since {ts_str})")
                last_alert_time = now

        elif num_faces == 0:
            last_face_center = None; block_start_time, static_image_start_time = None, None
            if no_face_start_time is None: no_face_start_time = datetime.datetime.now()
            ts_str = no_face_start_time.strftime("%H:%M:%S")
            status_text, color = f"ALERT: DRIVER MISSING since {ts_str}", (0, 0, 255)
            
            if now - last_alert_time > ALERT_REPEAT_SECS:
                alert_active_event.set()
                play_alert_sound(SOUND_NO_FACE_FREQ, SOUND_NO_FACE_DUR, alert_active_event, style=SOUND_NO_FACE_STYLE)
                log_event(f"Driver Missing Alert (since {ts_str})")
                last_alert_time = now

        else: # Face(s) are present, perform liveness checks
            alert_active_event.clear()
            block_start_time, no_face_start_time = None, None
            last_known_face_time = now
            
            (x, y, w, h) = max(faces, key=lambda rect: rect[2] * rect[3])
            
            # --- Liveness Factor 1: Blink Detection ---
            face_roi_gray = gray[y:y + h, x:x + w]
            eyes = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=EYE_SCALE_FACTOR, minNeighbors=EYE_MIN_NEIGHBORS, minSize=EYE_MIN_SIZE)
            if len(eyes) > 0:
                if BLINK_MIN_FRAMES <= no_eyes_counter <= BLINK_MAX_FRAMES:
                    last_blink_time = now
                no_eyes_counter = 0
            else:
                no_eyes_counter += 1

            # --- Liveness Factor 2: Motion Detection ---
            distance = 0
            current_face_center = (x + w // 2, y + h // 2)
            if last_face_center is not None:
                distance = math.sqrt((current_face_center[0] - last_face_center[0])**2 + (current_face_center[1] - last_face_center[1])**2)
                if distance > STATIC_MOVEMENT_THRESHOLD_PIXELS:
                    last_movement_time = now
            else:
                last_movement_time = now
            last_face_center = current_face_center

            # --- Final Liveness Decision ---
            no_blink_fail = (now - last_blink_time) > LIVENESS_TIMEOUT_SECS
            no_movement_fail = (now - last_movement_time) > LIVENESS_NO_MOVEMENT_SECS

            if no_blink_fail and no_movement_fail:
                if static_image_start_time is None: static_image_start_time = datetime.datetime.now()
                ts_str = static_image_start_time.strftime("%H:%M:%S")
                status_text, color = f"ALERT: STATIC IMAGE since {ts_str}", (0, 100, 255)
                
                if now - last_alert_time > ALERT_REPEAT_SECS:
                    alert_active_event.set()
                    play_alert_sound(SOUND_STATIC_FREQ, SOUND_STATIC_DUR, alert_active_event, style=SOUND_STATIC_STYLE)
                    log_event(f"Static Image Alert (since {ts_str})")
                    last_alert_time = now
            else:
                static_image_start_time = None
                status_text = "Status: OK | Driver Attentive"
                color = (0, 255, 0)
                # Enhanced debug output
                print(f"\r[DEBUG] MoveDist: {distance:<4.1f} | NoEyesFrames: {no_eyes_counter:<2}", end="")
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.imshow(WINDOW_TITLE, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("\n[INFO] Cleaning up...")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()