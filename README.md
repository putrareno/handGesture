# Hand Gesture Introduction

A Python-based hand gesture recognition application that uses a webcam to detect hand gestures and provides voice responses based on the detected gesture.

The application combines real-time hand tracking with Text-to-Speech (TTS) to create an interactive hand gesture introduction.

## Features

- Real-time hand gesture detection using a webcam
- Hand landmark detection using MediaPipe
- Gesture recognition for 5 different gestures
- Automatic voice response using Google Text-to-Speech
- Audio processing using Librosa
- Background audio playback using Pygame
- Stable gesture detection to prevent repeated voice responses
- Separate audio testing program

## Supported Gestures

| Gesture | Response |
|---|---|
| Open Palm | Hello! |
| Fist | My name is |
| Pointing | Putra |
| Peace | Reno |
| Three Fingers | Nice to meet you! |

The application waits for a gesture to remain stable for several frames before playing its corresponding audio response.

## Technologies

- Python
- OpenCV
- MediaPipe
- NumPy
- gTTS
- Librosa
- SoundFile
- Pygame
- Edge TTS
- Pydub

## Project Structure

```text
handGesture/
│
├── main.py
├── test_audio_only.py
├── requirements.txt
├── README.md
└── .gitignore
```

> Note: The `venv/`, `__pycache__/`, and `.pyc` files are not included in the repository because they are local Python environment and cache files.

## Requirements

Before running the project, make sure you have:

- Python 3.12
- Git
- A working webcam
- Speakers or headphones
- Internet connection

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/putrareno/handGesture.git
```

Then enter the project folder:

```bash
cd handGesture
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

#### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

Run the main application:

```bash
python main.py
```

The application will open the webcam and detect hand gestures in real time.

Press `Q` to quit the application.

## Audio Testing

The project also includes `test_audio_only.py` for testing the audio system separately without using the webcam or MediaPipe.

Run:

```bash
python test_audio_only.py
```

The program tests the following voice responses:

- Hello!
- My name is
- Putra
- Reno
- Nice to meet you!

## How It Works

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Detection
   ↓
Gesture Recognition
   ↓
Gesture Stabilization
   ↓
Audio Processing
   ↓
Pygame
   ↓
Voice Response
```

## Troubleshooting

### Camera Cannot Be Opened

Make sure your webcam is connected and is not being used by another application.

### MediaPipe Installation Error

Check your Python version:

```bash
python --version
```

This project is intended to run with Python 3.12.

### ModuleNotFoundError

Make sure the virtual environment is activated:

```powershell
venv\Scripts\Activate.ps1
```

Then install the dependencies again:

```bash
pip install -r requirements.txt
```

### Audio Does Not Play

Make sure your speakers or headphones are working and that you have an active internet connection.

You can test the audio separately using:

```bash
python test_audio_only.py
```

## Author

**Putra Reno**

GitHub: [putrareno](https://github.com/putrareno)