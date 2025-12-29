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

subtitle_Generator_app/
│
├── app.py
├── ui.py
├── video_selector.py
├── subtitle_processor.py
├── video_burner.py
├── progress.py
├── config.py
└── ffmpeg.exe