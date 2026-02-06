
import tkinter as tk
from tkinter import filedialog, messagebox
import whisper
from moviepy import VideoFileClip
import pysrt
import os
from tqdm import tqdm
import threading

# ==============================
# CONFIGURATION
# ==============================
VIDEO_PATH = "input_video.mp4"
OUTPUT_SRT = "output_subtitles.srt"
MODEL_SIZE = "base"  

# ==============================
# LOAD WHISPER MODEL
# ==============================
# Model	 | Parameters  | Relative Speed |
#--------|-------------|----------------|
# tiny	 | 39M	       | Fastest        |
# base	 | 74M	       | Fast           |
# small	 | 244M	       | Moderate       |
# medium | 769M	       | Slow           |
# large	 | 1550M	   | Slowest        |
print("🧠 Loading Whisper model...")
model = whisper.load_model(MODEL_SIZE)

# ==============================
# EXTRACT AUDIO FROM VIDEO
# ==============================
print("Extracting audio...")
video = VideoFileClip(VIDEO_PATH)
audio_path = "temp_audio.wav"
video.audio.write_audiofile(audio_path)
video.close()

# ==============================
# TRANSCRIBE & TRANSLATE
# ==============================
print("Transcribing & translating...")
result = model.transcribe(
    audio_path,
    task="translate",   # 👈 AUTO translate to English
    beam_size=5,
    verbose=True        # 👈 Shows progress during transcription
)


# ==============================
# CREATE SRT FILE
# ==============================
subs = pysrt.SubRipFile()
index = 1

print("Generating subtitle file...")
for segment in tqdm(result["segments"], desc="Writing subtitles"):
    start = segment["start"]
    end = segment["end"]
    text = segment["text"].strip()

    subs.append(
        pysrt.SubRipItem(
            index=index,
            start=pysrt.SubRipTime(seconds=start),
            end=pysrt.SubRipTime(seconds=end),
            text=text
        )
    )
    index += 1

subs.save(OUTPUT_SRT, encoding="utf-8")
os.remove(audio_path)

print("✅ SRT file created:", OUTPUT_SRT)
print("🌍 Detected language:", result["language"])
