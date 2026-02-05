import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
from moviepy import VideoFileClip
import pysrt
import os
from tqdm import tqdm
import threading


# Model	 | Parameters  | Relative Speed |
#--------|-------------|----------------|
# tiny	 | 39M	       | Fastest        |
# base	 | 74M	       | Fast           |
# small	 | 244M	       | Moderate       |
# medium | 769M	       | Slow           |
# large	 | 1550M	   | Slowest        |
MODEL_SIZE = "base"   

class SubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Subtitle Generator (Translate to English)")
        self.root.geometry("550x350")
        self.root.resizable(False, False)

        self.video_path = None

        tk.Label(
            root,
            text="Video Subtitle Generator",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.select_btn = tk.Button(
            root,
            text="Select Video File",
            command=self.select_video,
            width=35
        )
        self.select_btn.pack(pady=10)

        self.video_label = tk.Label(
            root,
            text="No file selected",
            fg="gray",
            wraplength=500
        )
        self.video_label.pack()

        self.generate_btn = tk.Button(
            root,
            text="Generate English Subtitles",
            command=self.start_generation,
            width=35,
            state="disabled"
        )
        self.generate_btn.pack(pady=15)

        # Progress bar
        self.progress = ttk.Progressbar(
            root,
            mode="indeterminate",
            length=400
        )
        self.progress.pack(pady=10)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack(pady=5)

    def select_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov *.flv"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.video_path = file_path
            self.video_label.config(
                text=os.path.basename(file_path),
                fg="black"
            )
            self.generate_btn.config(state="normal")

    def start_generation(self):
        self.generate_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
        self.status_label.config(text="Processing video... Please wait ⏳")
        self.progress.start(10)

        threading.Thread(target=self.generate_subtitles).start()

    def generate_subtitles(self):
        try:
            # Extract audio
            print("Extracting audio...")
            video = VideoFileClip(self.video_path)
            audio_path = "temp_audio.wav"
            video.audio.write_audiofile(audio_path, logger=None)
            video.close()

            # Load model
            print("🧠 Loading Whisper model...")
            model = whisper.load_model(MODEL_SIZE)

            # Transcribe & translate
            print("Transcribing & translating...")
            result = model.transcribe(
                audio_path,
                task="translate",  # 👈 AUTO translate to English
                beam_size=5,
                verbose=True         # 👈 Shows progress during transcription
            )

            # Create SRT
            srt_path = os.path.splitext(self.video_path)[0] + ".srt"
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

            subs.save(srt_path, encoding="utf-8")
            os.remove(audio_path)

            self.root.after(0, self.on_success, srt_path, result["language"])

        except Exception as e:
            self.root.after(0, self.on_error, str(e))

    def on_success(self, srt_path, language):
        self.progress.stop()
        self.status_label.config(
            text=f"✅ Done! Detected language: {language}"
        )
        self.generate_btn.config(state="normal")
        self.select_btn.config(state="normal")

        messagebox.showinfo(
            "Success",
            f"Subtitle file created:\n{srt_path}"
        )

    def on_error(self, error_msg):
        self.progress.stop()
        self.generate_btn.config(state="normal")
        self.select_btn.config(state="normal")
        messagebox.showerror("Error", error_msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleApp(root)
    root.mainloop()