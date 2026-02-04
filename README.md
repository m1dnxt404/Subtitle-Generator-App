# 🎬 AI Subtitle Generator & Translator

A Python application that automatically **generates subtitles (SRT)** from any video, **translates them into English**, and optionally **burns the subtitles into the video**.

✔ Supports any spoken language  
✔ Uses AI speech recognition  
✔ GUI for desktop usage   
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
- 🪟 Portable Windows executable (no installation required)

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
```

---

## 🛠️ Requirements

- Install Python **3.10 or higher**
- FFmpeg installed and available in system PATH
- Windows / Linux / macOS

---

## ⚙️ 1️⃣ Install Dependencies

```bash
pip install openai-whisper
```

```bash
pip install moviepy
```

```bash
pip install pysrt
```

```bash
pip install pyinstaller
```

```bash
pip install tdqm
```

## ▶️ Running the Application

```bash
python app.py
```

## 🖥 GUI Capabilities

The GUI allows you to:

- Select a video file
- Toggle Generate SRT
- Toggle Burn subtitles into video
- Customize subtitle style (font, size, color)
- View real-time progress (percentage)
- Automatically save output files

## 📂 Output Files

After processing, the following files may be generated in the same folder as the video:

```bash
video_name.srt
video_name_with_subs.mp4
```

## 🪟 Create Portable Windows EXE

You can package the application into a portable Windows executable using PyInstaller.

### Build EXE

```bash
pyinstaller --onefile --windowed app.py
```

The executable will be generated in the dist/ folder.

## ⚠️ Notes & Limitations

- Processing time depends on video length and hardware
- GPU acceleration is not enabled by default
- FFmpeg must be installed separately
- Long videos may require significant memory

## 🚀 Future Improvements

- GPU (CUDA) acceleration
- Batch processing for multiple videos
- Multi-language subtitle output
- Web-based interface

## 🙌 Acknowledgements

- OpenAI Whisper
- FFmpeg
- MoviePy
