# 🎬 AI Subtitle Generator & Translator

A Python application that automatically **generates subtitles (SRT)** from any video, **translates them into English**, and optionally **burns the subtitles into the video**.

✔ Supports any spoken language  
✔ Uses AI speech recognition  
✔ GUI for desktop usage  
✔ Dockerized CLI for automation  
✔ Portable Windows `.exe` support  

---

## ✨ Features

- 🎧 Automatic speech-to-text
- 🌍 Auto language detection + translation to English
- 📄 Generates `.srt` subtitle files
- 🎥 Burns subtitles directly into video
- 🎨 Custom subtitle styling (font, size, color)
- 📊 Determinate progress bar (percentage)
- 🖥 GUI (Tkinter)
- 🐳 Docker support (CLI mode)

---

## 📁 Project Structure

```graphql
│
├── app.py                 # Main entry point (UI startup)
├── ui.py                  # UI layout & widgets
├── video_selector.py      # Video file selection logic
├── subtitle_processor.py  # Whisper + SRT generation logic
├── video_burner.py        # FFmpeg subtitle burning logic
├── progress.py            # Progress bar updater
├── config.py              # App configuration
└── ffmpeg.exe             # (for portable EXE)         
