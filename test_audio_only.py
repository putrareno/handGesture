"""
TEST DIAGNOSTIK: putar ulang 5 kalimat gesture TANPA kamera/MediaPipe
sama sekali. Kalau di sini suaranya BERSIH (tidak patah-patah), berarti
penyebabnya adalah beban CPU dari OpenCV+MediaPipe yang bikin audio
buffer underrun saat main.py jalan. Kalau di sini juga MASIH
patah-patah, berarti masalahnya di proses slicing/pemotongan audio.

Cara pakai: jalankan file ini sendirian (python test_audio_only.py),
dengarkan baik-baik tiap kalimat yang diputar.
"""

import asyncio
import edge_tts
import pygame
import time
import os
import io
import tempfile
from pydub import AudioSegment

VOICE = "en-US-GuyNeural"
RATE = "+10%"
PITCH = "+0Hz"

messages = ["Hello!", "My name is", "Putra", "Reno", "Nice to meet you!"]

PAD_START = 0.03
PAD_END = 0.12

pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=4096)
pygame.mixer.init()


async def main():
    full_text = " ".join(messages)

    communicate = edge_tts.Communicate(full_text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")

    audio_bytes = b""
    word_boundaries = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            start = chunk["offset"] / 10_000_000
            duration = chunk["duration"] / 10_000_000
            word_boundaries.append((chunk["text"], start, start + duration))

    full_audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    total_duration_sec = len(full_audio) / 1000

    word_counts = [len(m.split()) for m in messages]
    print("Word boundaries terdeteksi:", [w[0] for w in word_boundaries])
    print("Word count per pesan:", word_counts, "total:", sum(word_counts))

    idx = 0
    clips = []
    for i, count in enumerate(word_counts):
        words_for_step = word_boundaries[idx: idx + count]
        idx += count

        start_s = max(0, words_for_step[0][1] - PAD_START)
        end_s = min(total_duration_sec, words_for_step[-1][2] + PAD_END)

        clip = full_audio[int(start_s * 1000): int(end_s * 1000)]
        clip = clip.fade_in(15).fade_out(30)

        filename = os.path.join(tempfile.gettempdir(), f"test_step_{i}.wav")
        clip.export(filename, format="wav")
        clips.append(filename)

    print()
    print("Memutar 5 klip satu per satu (jeda 1 detik antar klip)...")
    print("Dengarkan: apakah tiap kalimat terdengar MULUS atau PATAH-PATAH?")
    print()

    for i, (msg, filename) in enumerate(zip(messages, clips)):
        print(f"[{i+1}/5] Memutar: \"{msg}\"")
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.02)
        time.sleep(1)

    print()
    print("Selesai. Beri tahu Claude: bersih semua, atau ada yang masih patah?")

    for f in clips:
        try:
            os.remove(f)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
