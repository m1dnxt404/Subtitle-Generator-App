# 🎬 AI Subtitle Generator & Translator

A Python application that automatically **generates subtitles (SRT)** from any video, **translates them into 16+ languages**, and optionally **burns the subtitles into the video**.

- Supports any spoken language
- Uses AI speech recognition (OpenAI Whisper)
- Translate to English, Spanish, French, Japanese, and more
- GUI for desktop usage

---

## ✨ Features

- 🎧 Automatic speech-to-text
- 🌍 Auto language detection + translation to 16+ languages
- 📄 Generates `.srt` subtitle files
- 🎥 Burns subtitles directly into video (via FFmpeg)
- 🔤 Choose target language from a dropdown
- 🎨 Subtitle styling — font picker, text color picker, background box toggle
- 📊 Determinate progress bar (percentage)
- 🛑 Stop process at any time
- 🖥 Modern dark-themed GUI (CustomTkinter)

---

## 📁 Project Structure

```graphql

├── app.py                       # Entry point - launches the GUI
├── gui/
│   ├── __init__.py              # Re-exports SubtitleApp
│   └── gui.py                   # GUI layout, event handlers & logic
├── config/
│   ├── __init__.py              # Re-exports settings
│   └── settings.py              # App constants (models, formats, languages)
├── engine/
│   ├── __init__.py              # Re-exports SubtitleEngine
│   ├── engine.py                # Orchestrator - runs the full pipeline
│   ├── audio.py                 # Audio extraction from video
│   ├── transcribe.py            # Whisper model loading & transcription
│   ├── translate.py             # Post-translation via Google Translate
│   ├── srt.py                   # SRT subtitle file generation
│   └── burn.py                  # FFmpeg subtitle burning into video

```

---

## 🛠️ Requirements

- Python **3.10 or higher**
- FFmpeg installed and available in system PATH
- Windows / Linux / macOS

---

## ⚙️ Install Dependencies

```bash
pip install openai-whisper moviepy pysrt deep-translator customtkinter
```

Optional (for building a portable `.exe`):

```bash
pip install pyinstaller
```

---

## ▶️ Running the Application

```bash
python app.py
```

---

## 🖥 GUI

The application features a modern **dark-themed** interface built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), including:

- Card-style layout with rounded corners
- Select a video file (mp4, mkv, avi, mov, flv, wmv, webm, m4v, mpg, mpeg, 3gp, ts)
- Choose a Whisper model size (tiny → large)
- Choose a target language (English, Spanish, French, etc.)
- Toggle **Generate SRT file**
- Toggle **Burn subtitles into video**
- Or select **both** at the same time
- **Subtitle Style** panel:
  - Font picker — searchable dropdown of all installed system fonts
  - Text color picker — OS color dialog with live swatch preview
  - Background box toggle — adds a semi-transparent box behind subtitles
- Real-time progress bar with status updates
- Stop the process at any time
- Dark terminal-style log viewer

---

## 🌍 Supported Languages

| Language | Code |
| --- | --- |
| English | en |
| Spanish | es |
| French | fr |
| German | de |
| Portuguese | pt |
| Italian | it |
| Russian | ru |
| Chinese (Simplified) | zh-CN |
| Japanese | ja |
| Korean | ko |
| Arabic | ar |
| Hindi | hi |
| Turkish | tr |
| Dutch | nl |
| Polish | pl |
| Original (No Translation) | — |

- **English** uses Whisper's built-in translation (best quality)
- **Original** keeps the spoken language as-is (no translation)
- **Other languages** translate via Google Translate (requires `deep-translator`)

---

## 📂 Output Files

After processing, the following files may be generated in the output folder (or same folder as the video):

```bash
video_name.srt                # Subtitle file
video_name_subtitled.mp4      # Video with burned-in subtitles
```

---

## 🪟 Create Portable Windows EXE

You can package the application into a portable Windows executable using PyInstaller.

### Build EXE

```bash
pyinstaller --onefile --windowed app.py
```

The executable will be generated in the `dist/` folder.

---

## ⚠️ Notes & Limitations

- Processing time depends on video length and hardware
- GPU acceleration is not enabled by default
- FFmpeg must be installed separately for burning subtitles
- Long videos may require significant memory
- Non-English target languages require an internet connection (Google Translate)

---

## 🚀 Future Improvements

- GPU (CUDA) acceleration
- Batch processing for multiple videos
- Additional subtitle styling (opacity, line spacing, shadow strength)
- 🪟 Portable Windows executable (no installation required)
- Web-based interface

---

## 🙌 Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [FFmpeg](https://ffmpeg.org/)
- [MoviePy](https://zulko.github.io/moviepy/)
- [deep-translator](https://github.com/nidhaloff/deep-translator)
