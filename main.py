import cv2
import mediapipe as mp
import numpy as np
import threading
import queue
import os
import tempfile
import time

from gtts import gTTS
import librosa
import soundfile as sf
import pygame


CAMERA_INDEX = 0

# Google Translate-style TTS
LANGUAGE = "en"
TLD = "com"
TIME_STRETCH = 0.98

BASE_PITCH = 0.0

# Volume
VOLUME_GAIN = 0.0


REQUIRED_STABLE_FRAMES = 8

GESTURE_TEXT = {
    "OPEN_PALM": "Hello!",
    "FIST": "My name is",
    "POINTING": "Putra",
    "PEACE": "Reno",
    "THREE": "Nice to meet you!"
}

GESTURE_SPEECH = {
    "OPEN_PALM": "Hello!",
    "FIST": "My name is",
    "POINTING": "Putra",
    "PEACE": "Reno",
    "THREE": "Nice to meet you!"
}

INTONATION = {
    "OPEN_PALM": [
        -0.05,
         0.35,
         0.10
    ],

    "FIST": [
        -0.05,
         0.10,
         0.25,
         0.35
    ],

    "POINTING": [
        -0.05,
         0.20,
         0.45,
         0.20
    ],


    "PEACE": [
        -0.05,
         0.30,
         0.50,
         0.15
    ],

    "THREE": [
        -0.05,
         0.15,
         0.35,
         0.45,
         0.05
    ]
}


audio_cache = {}

def create_processed_audio(
    gesture,
    speech_text
):

    temp_mp3 = None
    temp_wav = None

    try:

        temp_mp3 = tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ).name

        temp_wav = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ).name

        print(
            f"[TTS] Membuat audio: {speech_text}"
        )

        tts = gTTS(
            text=speech_text,
            lang=LANGUAGE,
            tld=TLD,
            slow=False
        )

        tts.save(temp_mp3)

        y, sr = librosa.load(
            temp_mp3,
            sr=22050,
            mono=True
        )

        y = librosa.effects.time_stretch(
            y,
            rate=TIME_STRETCH
        )

        pitch_values = {

            # Hello!
            "OPEN_PALM": 0.05,

            # My name is
            "FIST": 0.00,

            # Putra
            "POINTING": 0.08,

            # Reno
            "PEACE": 0.10,

            # Nice to meet you!
            "THREE": 0.05
        }

        pitch = (
            pitch_values.get(
                gesture,
                0.0
            )
            + BASE_PITCH
        )

        # Hanya proses pitch jika memang diperlukan
        if abs(pitch) > 0.001:

            y = librosa.effects.pitch_shift(
                y,
                sr=sr,
                n_steps=pitch
            )

        peak = np.max(
            np.abs(y)
        )

        if peak > 0:

            target_peak = 0.90

            y = (
                y
                / peak
                * target_peak
            )

        gain = 10 ** (
            VOLUME_GAIN / 20
        )

        y = y * gain

        max_value = np.max(
            np.abs(y)
        )

        if max_value > 1.0:

            y = (
                y
                / max_value
                * 0.98
            )

        y = np.clip(
            y,
            -1.0,
            1.0
        )

        sf.write(
            temp_wav,
            y,
            sr
        )

        try:

            os.remove(
                temp_mp3
            )

        except:

            pass

        temp_mp3 = None

        return temp_wav

    except Exception as e:

        print(
            f"[ERROR AUDIO] {gesture}: {e}"
        )

        if temp_mp3:

            try:

                os.remove(
                    temp_mp3
                )

            except:

                pass

        if temp_wav:

            try:

                os.remove(
                    temp_wav
                )

            except:

                pass

        return None

def preload_audio():

    print()
    print("=" * 55)
    print("MENYIAPKAN AUDIO...")
    print("=" * 55)
    print()

    for gesture in GESTURE_TEXT:

        message = GESTURE_TEXT[
            gesture
        ]

        speech = GESTURE_SPEECH[
            gesture
        ]

        print(
            f"[{gesture}]"
        )

        print(
            f"  Text   : {message}"
        )

        print(
            f"  Speech : {speech}"
        )

        audio_file = create_processed_audio(
            gesture,
            speech
        )

        if audio_file:

            audio_cache[
                gesture
            ] = audio_file

            print(
                "  ✓ Audio siap"
            )

        else:

            print(
                "  ✗ Audio gagal"
            )

        print()

    print("=" * 55)

    if len(audio_cache) == len(
        GESTURE_TEXT
    ):

        print(
            "✓ SEMUA AUDIO SUDAH SIAP"
        )

    else:

        print(
            "⚠ Ada audio yang gagal dibuat"
        )

    print("=" * 55)
    print()


audio_queue = queue.Queue()

def audio_worker():

    while True:

        gesture = audio_queue.get()

        if gesture is None:

            audio_queue.task_done()

            break

        try:

            audio_file = audio_cache.get(
                gesture
            )

            if audio_file is not None:

                pygame.mixer.music.load(
                    audio_file
                )

                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():

                    time.sleep(
                        0.01
                    )

        except Exception as e:

            print(
                f"[PLAYBACK ERROR] {e}"
            )

        finally:

            audio_queue.task_done()

pygame.mixer.init(
    frequency=22050,
    size=-16,
    channels=1,
    buffer=512
)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

def detect_gesture(
    hand_landmarks
):

    lm = hand_landmarks.landmark

    index_up = (
        lm[8].y < lm[6].y
    )

    middle_up = (
        lm[12].y < lm[10].y
    )

    ring_up = (
        lm[16].y < lm[14].y
    )

    pinky_up = (
        lm[20].y < lm[18].y
    )

    thumb_up = (
        lm[4].y < lm[3].y
    )

    if (
        thumb_up
        and index_up
        and not middle_up
        and not ring_up
        and pinky_up
    ):

        return "THREE"

    if (
        thumb_up
        and index_up
        and middle_up
        and ring_up
        and pinky_up
    ):

        return "OPEN_PALM"

    if (
        not index_up
        and not middle_up
        and not ring_up
        and not pinky_up
    ):

        return "FIST"

    if (
        index_up
        and not middle_up
        and not ring_up
        and not pinky_up
    ):

        return "POINTING"

    if (
        index_up
        and middle_up
        and not ring_up
        and not pinky_up
    ):

        return "PEACE"

    return None


print()
print("==============================================")
print(" HAND GESTURE INTRODUCTION")
print("==============================================")
print()

preload_audio()

audio_thread = threading.Thread(
    target=audio_worker,
    daemon=True
)

audio_thread.start()

cap = cv2.VideoCapture(
    CAMERA_INDEX
)

if not cap.isOpened():

    print(
        "ERROR: Kamera tidak dapat dibuka."
    )

    audio_queue.put(
        None
    )

    pygame.mixer.quit()

    raise SystemExit


current_gesture = None

stable_gesture = None

stable_frames = 0

last_spoken_gesture = None

try:

    while True:

        ret, frame = cap.read()

        if not ret:

            print(
                "Tidak dapat membaca kamera."
            )

            break

        frame = cv2.flip(
            frame,
            1
        )

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = hands.process(
            rgb
        )

        detected_gesture = None

        if results.multi_hand_landmarks:

            hand_landmarks = (
                results.multi_hand_landmarks[0]
            )

            detected_gesture = detect_gesture(
                hand_landmarks
            )

            # Draw landmarks
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

        if (
            detected_gesture
            == current_gesture
        ):

            stable_frames += 1

        else:

            current_gesture = (
                detected_gesture
            )

            stable_frames = 0

        if (
            current_gesture is not None
            and
            stable_frames
            >= REQUIRED_STABLE_FRAMES
        ):

            if (
                current_gesture
                != last_spoken_gesture
            ):

                if (
                    current_gesture
                    in audio_cache
                ):

                    audio_queue.put(
                        current_gesture
                    )

                    print(
                        f"[GESTURE] "
                        f"{current_gesture} "
                        f"-> "
                        f"{GESTURE_TEXT[current_gesture]}"
                    )

                    last_spoken_gesture = (
                        current_gesture
                    )

        if detected_gesture is None:

            current_gesture = None

            stable_frames = 0

            last_spoken_gesture = None

        if current_gesture:

            display_gesture = (
                current_gesture
            )

            display_text = (
                GESTURE_TEXT[
                    current_gesture
                ]
            )

        else:

            display_gesture = (
                "No Gesture"
            )

            display_text = ""

        # Gesture
        cv2.putText(
            frame,
            f"Gesture: {display_gesture}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

        # Text
        if display_text:

            cv2.putText(
                frame,
                display_text,
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        # Status audio
        cv2.putText(
            frame,
            "Audio: READY",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )

        # Quit
        cv2.putText(
            frame,
            "Press Q to quit",
            (
                20,
                frame.shape[0] - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Hand Gesture Introduction",
            frame
        )

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        if key == ord("q"):

            break

finally:
    print()
    print(
        "Menutup program..."
    )

    # Camera
    cap.release()

    cv2.destroyAllWindows()

    hands.close()

    # Tunggu audio yang sedang antre
    audio_queue.join()

    # Stop audio worker
    audio_queue.put(
        None
    )

    audio_thread.join(
        timeout=2
    )

    # Stop pygame
    pygame.mixer.quit()

    for audio_file in audio_cache.values():

        try:

            if os.path.exists(
                audio_file
            ):

                os.remove(
                    audio_file
                )

        except:

            pass

    print(
        "Program selesai."
    )