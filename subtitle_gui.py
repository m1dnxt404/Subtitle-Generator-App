import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
from moviepy import VideoFileClip
import pysrt
import os
import sys
import threading
import subprocess


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
        self.root.geometry("550x670")
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

        video_frame = tk.Frame(root)
        video_frame.pack(pady=10, padx=15, fill="x")
        self.select_btn = tk.Button(
            video_frame,
            text="Select Video File",
            command=self.select_video,
            width=18
        )
        self.select_btn.pack(side="left")
        self.video_var = tk.StringVar(value="No file selected")
        self.video_entry = tk.Entry(
            video_frame,
            textvariable=self.video_var,
            state="readonly",
            readonlybackground="white",
            fg="gray"
        )
        self.video_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)

        output_frame = tk.Frame(root)
        output_frame.pack(pady=(0, 10), padx=15, fill="x")
        self.output_btn = tk.Button(
            output_frame,
            text="Select Output Folder",
            command=self.select_output,
            width=18
        )
        self.output_btn.pack(side="left")
        self.output_var = tk.StringVar(value="Same folder as video")
        self.output_entry = tk.Entry(
            output_frame,
            textvariable=self.output_var,
            state="readonly",
            readonlybackground="white",
            fg="gray"
        )
        self.output_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)

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

        # Output options checkboxes
        options_frame = tk.LabelFrame(root, text="Output Options", padx=10, pady=5)
        options_frame.pack(pady=10, padx=15, fill="x")

        self.srt_var = tk.BooleanVar(value=True)
        self.burn_var = tk.BooleanVar(value=False)

        self.srt_check = tk.Checkbutton(
            options_frame,
            text="Generate SRT file",
            variable=self.srt_var,
            command=self._validate_options
        )
        self.srt_check.pack(anchor="w")

        self.burn_check = tk.Checkbutton(
            options_frame,
            text="Burn subtitles into video",
            variable=self.burn_var,
            command=self._validate_options
        )
        self.burn_check.pack(anchor="w")

        self.generate_btn = tk.Button(
            root,
            text="Generate",
            command=self.start_generation,
            width=35,
            state="disabled"
        )
        self.generate_btn.pack(pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            root,
            mode="determinate",
            length=400,
            maximum=100,
            variable=self.progress_var
        )
        self.progress.pack(pady=(10, 0))

        self.progress_label = tk.Label(root, text="0%", fg="gray")
        self.progress_label.pack()

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

    def _update_progress(self, value, status_text=None):
        self.root.after(0, self._set_progress, value, status_text)

    def _set_progress(self, value, status_text):
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        if status_text:
            self.status_label.config(text=status_text)

    def _validate_options(self):
        if self.video_path and (self.srt_var.get() or self.burn_var.get()):
            self.generate_btn.config(state="normal")
        else:
            self.generate_btn.config(state="disabled")

    def select_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov *.flv"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.video_path = file_path
            self.video_var.set(os.path.basename(file_path))
            self.video_entry.config(fg="black")
            self._validate_options()

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.output_var.set(folder)
            self.output_entry.config(fg="black")

    def start_generation(self):
        if not self.srt_var.get() and not self.burn_var.get():
            messagebox.showwarning("No option selected", "Please select at least one output option.")
            return

        self._stop_event.clear()
        self.generate_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
        self.output_btn.config(state="disabled")
        self.model_combo.config(state="disabled")
        self.srt_check.config(state="disabled")
        self.burn_check.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.status_label.config(text="Processing video... Please wait")

        threading.Thread(target=self.generate_subtitles).start()

    def stop_generation(self):
        self._stop_event.set()
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Stopping...")

    def generate_subtitles(self):
        audio_path = "temp_audio.wav"
        do_srt = self.srt_var.get()
        do_burn = self.burn_var.get()

        try:
            # Extract audio (0% -> 10%)
            self._update_progress(0, "Extracting audio...")
            print("Extracting audio...")
            video = VideoFileClip(self.video_path)
            video.audio.write_audiofile(audio_path, logger=None)
            video.close()
            self._update_progress(10)

            if self._stop_event.is_set():
                raise InterruptedError("Process stopped by user.")

            # Load model (10% -> 25%)
            self._update_progress(10, "Loading Whisper model...")
            print("Loading Whisper model...")
            model_size = MODEL_OPTIONS[self.model_var.get()]
            model = whisper.load_model(model_size)
            self._update_progress(25)

            if self._stop_event.is_set():
                raise InterruptedError("Process stopped by user.")

            # Transcribe & translate (25% -> 70%)
            self._update_progress(25, "Transcribing & translating...")
            print("Transcribing & translating...")
            result = model.transcribe(
                audio_path,
                task="translate",
                beam_size=5,
                verbose=True
            )
            self._update_progress(70)

            if self._stop_event.is_set():
                raise InterruptedError("Process stopped by user.")

            # Build SRT content (70% -> 80%)
            self._update_progress(70, "Building subtitle data...")
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            if self.output_dir:
                srt_path = os.path.join(self.output_dir, video_name + ".srt")
            else:
                srt_path = os.path.splitext(self.video_path)[0] + ".srt"

            subs = pysrt.SubRipFile()
            segments = result["segments"]
            total = len(segments)
            print(f"Processing segments... ({total} segments)")
            for i, segment in enumerate(segments):
                if self._stop_event.is_set():
                    raise InterruptedError("Process stopped by user.")
                subs.append(
                    pysrt.SubRipItem(
                        index=i + 1,
                        start=pysrt.SubRipTime(seconds=segment["start"]),
                        end=pysrt.SubRipTime(seconds=segment["end"]),
                        text=segment["text"].strip()
                    )
                )
                self._update_progress(70 + (i + 1) / total * 10)

            # Save SRT file (always needed for burn, optionally kept)
            subs.save(srt_path, encoding="utf-8")
            self._update_progress(80)

            if self._stop_event.is_set():
                raise InterruptedError("Process stopped by user.")

            # Burn subtitles into video (80% -> 95%)
            output_video_path = None
            if do_burn:
                self._update_progress(80, "Burning subtitles into video...")
                print("Burning subtitles into video (ffmpeg)...")

                ext = os.path.splitext(self.video_path)[1]
                if self.output_dir:
                    output_video_path = os.path.join(
                        self.output_dir, video_name + "_subtitled" + ext
                    )
                else:
                    output_video_path = os.path.splitext(self.video_path)[0] + "_subtitled" + ext

                # Use ffmpeg to burn subtitles
                srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
                cmd = [
                    "ffmpeg", "-y",
                    "-i", self.video_path,
                    "-vf", f"subtitles='{srt_escaped}'",
                    "-c:a", "copy",
                    output_video_path
                ]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in process.stdout:
                    if self._stop_event.is_set():
                        process.kill()
                        raise InterruptedError("Process stopped by user.")
                    line = line.strip()
                    if line.startswith("frame="):
                        print(line)
                process.wait()

                if process.returncode != 0:
                    raise RuntimeError("ffmpeg failed to burn subtitles. Make sure ffmpeg is installed and in PATH.")

                print("Subtitles burned successfully.")
                self._update_progress(95)

            # Clean up SRT if user only wanted burn
            if not do_srt and do_burn:
                os.remove(srt_path)
                srt_path = None

            os.remove(audio_path)
            self._update_progress(100, "Complete!")

            self.root.after(0, self.on_success, srt_path, output_video_path, result["language"])

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
        self.srt_check.config(state="normal")
        self.burn_check.config(state="normal")

    def on_success(self, srt_path, output_video_path, language):
        self._reset_controls()
        self.status_label.config(
            text=f"Done! Detected language: {language}"
        )
        msg_parts = []
        if srt_path:
            msg_parts.append(f"SRT file:\n{srt_path}")
        if output_video_path:
            msg_parts.append(f"Video with subtitles:\n{output_video_path}")
        messagebox.showinfo("Success", "\n\n".join(msg_parts))

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