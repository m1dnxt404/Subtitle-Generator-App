import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import threading
from config import MODEL_OPTIONS, SUPPORTED_VIDEO_FORMATS, WINDOW_TITLE, WINDOW_SIZE, LANGUAGE_OPTIONS
from subtitle_engine import SubtitleEngine


class SubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.original_stdout = sys.stdout

        self.video_path = None
        self.output_dir = None
        self._stop_event = threading.Event()

        self._build_header()
        self._build_file_selection()
        self._build_model_selector()
        self._build_language_selector()
        self._build_output_options()
        self._build_generate_button()
        self._build_progress_section()
        self._build_log_section()

        sys.stdout = self

    # ── UI Builder Methods ──────────────────────────────────────────

    def _build_header(self):
        tk.Label(
            self.root,
            text="Video Subtitle Generator",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

    def _build_file_selection(self):
        # Video file selector
        video_frame = tk.Frame(self.root)
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

        # Output folder selector
        output_frame = tk.Frame(self.root)
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

    def _build_model_selector(self):
        model_frame = tk.Frame(self.root)
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

    def _build_language_selector(self):
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=(0, 10))

        tk.Label(lang_frame, text="Translate to:").pack(side="left", padx=(0, 5))

        self.lang_var = tk.StringVar(value="English")
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=list(LANGUAGE_OPTIONS.keys()),
            state="readonly",
            width=30
        )
        self.lang_combo.pack(side="left")

    def _build_output_options(self):
        options_frame = tk.LabelFrame(
            self.root, text="Output Options", padx=10, pady=5
        )
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

    def _build_generate_button(self):
        self.generate_btn = tk.Button(
            self.root,
            text="Generate",
            command=self.start_generation,
            width=35,
            state="disabled"
        )
        self.generate_btn.pack(pady=10)

    def _build_progress_section(self):
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            self.root,
            mode="determinate",
            length=400,
            maximum=100,
            variable=self.progress_var
        )
        self.progress.pack(pady=(10, 0))

        self.progress_label = tk.Label(self.root, text="0%", fg="gray")
        self.progress_label.pack()

        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=5)

        self.stop_btn = tk.Button(
            self.root,
            text="Stop Process",
            command=self.stop_generation,
            fg="white",
            bg="#cc0000",
            state="disabled",
            width=12
        )
        self.stop_btn.pack(anchor="e", padx=15)

    def _build_log_section(self):
        log_frame = tk.LabelFrame(self.root, text="Logs", padx=5, pady=5)
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

    # ── Stdout Redirect ─────────────────────────────────────────────

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

    # ── Progress ─────────────────────────────────────────────────────

    def _on_progress(self, value, status_text=None):
        self.root.after(0, self._set_progress, value, status_text)

    def _set_progress(self, value, status_text):
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        if status_text:
            self.status_label.config(text=status_text)

    # ── Event Handlers ───────────────────────────────────────────────

    def _validate_options(self):
        if self.video_path and (self.srt_var.get() or self.burn_var.get()):
            self.generate_btn.config(state="normal")
        else:
            self.generate_btn.config(state="disabled")

    def select_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video Files", SUPPORTED_VIDEO_FORMATS),
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
            messagebox.showwarning(
                "No option selected",
                "Please select at least one output option."
            )
            return

        self._stop_event.clear()
        self._set_controls_locked(True)

        threading.Thread(target=self._run_generation).start()

    def stop_generation(self):
        self._stop_event.set()
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Stopping...")

    # ── Generation Thread ────────────────────────────────────────────

    def _resolve_output_paths(self):
        video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        ext = os.path.splitext(self.video_path)[1]

        if self.output_dir:
            srt_path = os.path.join(self.output_dir, video_name + ".srt")
            video_out = os.path.join(
                self.output_dir, video_name + "_subtitled" + ext
            )
        else:
            base = os.path.splitext(self.video_path)[0]
            srt_path = base + ".srt"
            video_out = base + "_subtitled" + ext

        return srt_path, video_out

    def _run_generation(self):
        do_srt = self.srt_var.get()
        do_burn = self.burn_var.get()
        srt_path, output_video_path = self._resolve_output_paths()

        engine = SubtitleEngine(
            progress_callback=self._on_progress,
            stop_check=self._stop_event.is_set
        )

        try:
            srt_path, output_video_path, language = engine.generate(
                video_path=self.video_path,
                model_size=MODEL_OPTIONS[self.model_var.get()],
                srt_path=srt_path,
                target_language=LANGUAGE_OPTIONS[self.lang_var.get()],
                output_video_path=output_video_path if do_burn else None,
                do_srt=do_srt,
                do_burn=do_burn
            )
            self.root.after(
                0, self._on_success, srt_path, output_video_path, language
            )

        except InterruptedError:
            print("Process stopped.")
            self.root.after(0, self._on_stopped)

        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    # ── Control State ────────────────────────────────────────────────

    def _set_controls_locked(self, locked):
        state = "disabled" if locked else "normal"
        combo_state = "disabled" if locked else "readonly"
        stop_state = "normal" if locked else "disabled"

        self.generate_btn.config(state=state)
        self.select_btn.config(state=state)
        self.output_btn.config(state=state)
        self.srt_check.config(state=state)
        self.burn_check.config(state=state)
        self.model_combo.config(state=combo_state)
        self.lang_combo.config(state=combo_state)
        self.stop_btn.config(state=stop_state)

        if locked:
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            self.status_label.config(text="Processing video... Please wait")

    # ── Completion Callbacks ─────────────────────────────────────────

    def _on_success(self, srt_path, output_video_path, language):
        self._set_controls_locked(False)
        self.status_label.config(text=f"Done! Detected language: {language}")

        msg_parts = []
        if srt_path:
            msg_parts.append(f"SRT file:\n{srt_path}")
        if output_video_path:
            msg_parts.append(f"Video with subtitles:\n{output_video_path}")
        messagebox.showinfo("Success", "\n\n".join(msg_parts))

    def _on_stopped(self):
        self._set_controls_locked(False)
        self.status_label.config(text="Stopped by user.")

    def _on_error(self, error_msg):
        self._set_controls_locked(False)
        messagebox.showerror("Error", error_msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleApp(root)
    root.mainloop()
