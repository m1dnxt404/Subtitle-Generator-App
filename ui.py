import tkinter as tk
from tkinter import ttk, messagebox
from video_selector import select_video
from subtitle_processor import generate_subtitles
from video_burner import burn_subtitles
import threading

class SubtitleUI:
    def __init__(self, root):
        self.root = root
        self.video_path = None

        root.title("Video Subtitle Generator")
        root.geometry("640x430")
        root.resizable(False, False)

        tk.Label(root, text="Video Subtitle Generator", font=("Arial", 16, "bold")).pack(pady=10)

        self.select_btn = tk.Button(root, text="Select Video File", width=45, command=self.on_select)
        self.select_btn.pack(pady=8)

        self.video_label = tk.Label(root, text="No file selected", fg="gray", wraplength=600)
        self.video_label.pack()

        self.gen_srt = tk.BooleanVar(value=True)
        self.burn = tk.BooleanVar(value=True)

        frame = tk.Frame(root)
        frame.pack(pady=10)
        tk.Checkbutton(frame, text="Generate SRT", variable=self.gen_srt).grid(row=0, column=0, padx=15)
        tk.Checkbutton(frame, text="Burn subtitles", variable=self.burn).grid(row=0, column=1, padx=15)

        self.start_btn = tk.Button(root, text="Start Processing", width=45, state="disabled", command=self.start)
        self.start_btn.pack(pady=10)

        self.progress = ttk.Progressbar(root, mode="determinate", length=500)
        self.progress.pack(pady=10)

        self.percent = tk.Label(root, text="0%")
        self.percent.pack()

    def on_select(self):
        self.video_path = select_video(self.video_label, lambda: self.start_btn.config(state="normal"))

    def update_progress(self, value):
        self.progress["value"] = value
        self.percent.config(text=f"{int(value)}%")
        self.root.update_idletasks()

    def start(self):
        if not self.gen_srt.get() and not self.burn.get():
            messagebox.showwarning("Select option", "Please select at least one option.")
            return
        self.start_btn.config(state="disabled")
        threading.Thread(target=self.process).start()

    def process(self):
        try:
            srt_path, language = generate_subtitles(self.video_path, self.update_progress)
            if self.burn.get():
                burn_subtitles(self.video_path, srt_path)
            messagebox.showinfo("Success", f"Done!\nDetected language: {language}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.start_btn.config(state="normal")
