import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
from moviepy import VideoFileClip
import pysrt
import os
import sys
from tqdm import tqdm
import threading


# Model	 | Parameters  | Relative Speed |
#--------|-------------|----------------|
# tiny	 | 39M	       | Fastest        |
# base	 | 74M	       | Fast           |
# small	 | 244M	       | Moderate       |
# medium | 769M	       | Slow           |
# large	 | 1550M	   | Slowest        |
MODEL_OPTIONS = {
    "tiny (39M - Fastest)": "tiny",
    "base (74M - Fast)": "base",
    "small (244M - Moderate)": "small",
    "medium (769M - Slow)": "medium",
    "large (1550M - Slowest)": "large",
}

class SubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Subtitle Generator (Translate to English)")
        self.root.geometry("550x600")
        self.root.resizable(False, False)
        self.original_stdout = sys.stdout

        self.video_path = None
        self.output_dir = None
        self._stop_event = threading.Event()

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

        self.output_btn = tk.Button(
            root,
            text="Select Output Folder",
            command=self.select_output,
            width=35
        )
        self.output_btn.pack(pady=(10, 0))

        self.output_label = tk.Label(
            root,
            text="Default: same folder as video",
            fg="gray",
            wraplength=500
        )
        self.output_label.pack()

        # Model size selector
        model_frame = tk.Frame(root)
        model_frame.pack(pady=10)
        tk.Label(model_frame, text="Model:").pack(side="left", padx=(0, 5))
        self.model_var = tk.StringVar(value="base (74M - Fast)")
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=list(MODEL_OPTIONS.keys()),
            state="readonly",
            width=30
        )
        self.model_combo.pack(side="left")

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

        # Stop button
        self.stop_btn = tk.Button(
            root,
            text="Stop Process",
            command=self.stop_generation,
            fg="white",
            bg="#cc0000",
            state="disabled",
            width=12
        )
        self.stop_btn.pack(anchor="e", padx=15)

        # Log container
        log_frame = tk.LabelFrame(root, text="Logs", padx=5, pady=5)
        log_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        self.log_text = tk.Text(
            log_frame,
            height=8,
            wrap="word",
            state="disabled",
            bg="#1e1e1e",
            fg="#cccccc",
            font=("Consolas", 9)
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=log_scroll.set)

        sys.stdout = self

    def write(self, text):
        self.original_stdout.write(text)
        self.root.after(0, self._append_log, text)

    def flush(self):
        self.original_stdout.flush()

    def _append_log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

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

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.output_label.config(text=folder, fg="black")

    def start_generation(self):
        self._stop_event.clear()
        self.generate_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
        self.output_btn.config(state="disabled")
        self.model_combo.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Processing video... Please wait ⏳")
        self.progress.start(10)

        threading.Thread(target=self.generate_subtitles).start()

    def stop_generation(self):
        self._stop_event.set()
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Stopping...")

    def generate_subtitles(self):
        audio_path = "temp_audio.wav"
        try:
            # Extract audio
            print("Extracting audio...")
            video = VideoFileClip(self.video_path)
            video.audio.write_audiofile(audio_path, logger=None)
            video.close()

            if self._stop_event.is_set():
                raise InterruptedError("Process stopped by user.")

            # Load model
            print("🧠 Loading Whisper model...")
            model_size = MODEL_OPTIONS[self.model_var.get()]
            model = whisper.load_model(model_size)

            if self._stop_event.is_set():
                raise InterruptedError("Process stopped by user.")

            # Transcribe & translate
            print("Transcribing & translating...")
            result = model.transcribe(
                audio_path,
                task="translate",  # 👈 AUTO translate to English
                beam_size=5,
                verbose=True         # 👈 Shows progress during transcription
            )

            if self._stop_event.is_set():
                raise InterruptedError("Process stopped by user.")

            # Create SRT
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            if self.output_dir:
                srt_path = os.path.join(self.output_dir, video_name + ".srt")
            else:
                srt_path = os.path.splitext(self.video_path)[0] + ".srt"
            subs = pysrt.SubRipFile()
            index = 1

            print("Generating subtitle file...")
            for segment in tqdm(result["segments"], desc="Writing subtitles"):
                if self._stop_event.is_set():
                    raise InterruptedError("Process stopped by user.")
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

        except InterruptedError:
            print("Process stopped.")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            self.root.after(0, self.on_stopped)

        except Exception as e:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            self.root.after(0, self.on_error, str(e))

    def _reset_controls(self):
        self.generate_btn.config(state="normal")
        self.select_btn.config(state="normal")
        self.output_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.model_combo.config(state="readonly")
        self.progress.stop()

    def on_success(self, srt_path, language):
        self._reset_controls()
        self.status_label.config(
            text=f"✅ Done! Detected language: {language}"
        )
        messagebox.showinfo(
            "Success",
            f"Subtitle file created:\n{srt_path}"
        )

    def on_stopped(self):
        self._reset_controls()
        self.status_label.config(text="Stopped by user.")

    def on_error(self, error_msg):
        self._reset_controls()
        messagebox.showerror("Error", error_msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleApp(root)
    root.mainloop()