import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter.colorchooser import askcolor
from tkinter.font import families as tk_font_families
import os
import sys
import threading

from config import MODEL_OPTIONS, SUPPORTED_VIDEO_FORMATS, WINDOW_TITLE, WINDOW_SIZE, LANGUAGE_OPTIONS
from engine import SubtitleEngine


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
        self._build_settings()
        self._build_output_options()
        self._build_subtitle_style()
        self._build_generate_button()
        self._build_progress_section()
        self._build_log_section()

        sys.stdout = self

    # ── UI Builder Methods ──────────────────────────────────────────

    def _build_header(self):
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(18, 6))

        ctk.CTkLabel(
            header_frame,
            text="Video Subtitle Generator",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Generate and burn subtitles powered by OpenAI Whisper",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        ).pack(anchor="w", pady=(2, 0))

    def _build_file_selection(self):
        card = ctk.CTkFrame(self.root, corner_radius=10)
        card.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(
            card,
            text="Input / Output",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Video file row
        video_row = ctk.CTkFrame(card, fg_color="transparent")
        video_row.pack(fill="x", padx=16, pady=(0, 8))

        self.select_btn = ctk.CTkButton(
            video_row,
            text="Select Video File",
            command=self.select_video,
            width=160,
            height=32,
        )
        self.select_btn.pack(side="left")

        self.video_var = ctk.StringVar(value="")
        self.video_entry = ctk.CTkEntry(
            video_row,
            textvariable=self.video_var,
            placeholder_text="No file selected",
            state="disabled",
            height=32,
        )
        self.video_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Output folder row
        output_row = ctk.CTkFrame(card, fg_color="transparent")
        output_row.pack(fill="x", padx=16, pady=(0, 14))

        self.output_btn = ctk.CTkButton(
            output_row,
            text="Select Output Folder",
            command=self.select_output,
            width=160,
            height=32,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a",
        )
        self.output_btn.pack(side="left")

        self.output_var = ctk.StringVar(value="")
        self.output_entry = ctk.CTkEntry(
            output_row,
            textvariable=self.output_var,
            placeholder_text="Same folder as video",
            state="disabled",
            height=32,
        )
        self.output_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)

    def _build_settings(self):
        card = ctk.CTkFrame(self.root, corner_radius=10)
        card.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            card,
            text="Settings",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(12, 8))

        settings_grid = ctk.CTkFrame(card, fg_color="transparent")
        settings_grid.pack(fill="x", padx=16, pady=(0, 14))
        settings_grid.columnconfigure(1, weight=1)

        # Model selector
        ctk.CTkLabel(
            settings_grid,
            text="Model:",
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 8))

        self.model_var = ctk.StringVar(value="base (74M - Fast)")
        self.model_combo = ctk.CTkOptionMenu(
            settings_grid,
            variable=self.model_var,
            values=list(MODEL_OPTIONS.keys()),
            width=300,
            height=32,
        )
        self.model_combo.grid(row=0, column=1, sticky="ew", pady=(0, 8))

        # Language selector
        ctk.CTkLabel(
            settings_grid,
            text="Translate to:",
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="w", padx=(0, 12))

        self.lang_var = ctk.StringVar(value="English")
        self.lang_combo = ctk.CTkOptionMenu(
            settings_grid,
            variable=self.lang_var,
            values=list(LANGUAGE_OPTIONS.keys()),
            width=300,
            height=32,
        )
        self.lang_combo.grid(row=1, column=1, sticky="ew")

    def _build_output_options(self):
        card = ctk.CTkFrame(self.root, corner_radius=10)
        card.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            card,
            text="Output Options",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(12, 8))

        options_inner = ctk.CTkFrame(card, fg_color="transparent")
        options_inner.pack(fill="x", padx=16, pady=(0, 14))

        self.srt_var = ctk.BooleanVar(value=True)
        self.burn_var = ctk.BooleanVar(value=False)

        self.srt_check = ctk.CTkCheckBox(
            options_inner,
            text="Generate SRT file",
            variable=self.srt_var,
            command=self._validate_options,
            font=ctk.CTkFont(size=13),
        )
        self.srt_check.pack(anchor="w", pady=(0, 6))

        self.burn_check = ctk.CTkCheckBox(
            options_inner,
            text="Burn subtitles into video",
            variable=self.burn_var,
            command=self._validate_options,
            font=ctk.CTkFont(size=13),
        )
        self.burn_check.pack(anchor="w")

    def _build_subtitle_style(self):
        card = ctk.CTkFrame(self.root, corner_radius=10)
        card.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            card,
            text="Subtitle Style",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(12, 8))

        style_grid = ctk.CTkFrame(card, fg_color="transparent")
        style_grid.pack(fill="x", padx=16, pady=(0, 14))
        style_grid.columnconfigure(1, weight=1)

        # ── Font row ──
        ctk.CTkLabel(
            style_grid,
            text="Font:",
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))

        system_fonts = sorted(set(tk_font_families()))
        default_font = "Arial" if "Arial" in system_fonts else system_fonts[0]

        self.font_var = ctk.StringVar(value=default_font)
        self.font_combo = ctk.CTkComboBox(
            style_grid,
            variable=self.font_var,
            values=system_fonts,
            height=32,
        )
        self.font_combo.grid(row=0, column=1, sticky="ew")

        # ── Text color row ──
        ctk.CTkLabel(
            style_grid,
            text="Text Color:",
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=(8, 0))

        self.primary_color_hex = "#FFFFFF"
        self.color_btn = ctk.CTkButton(
            style_grid,
            text=self.primary_color_hex,
            width=130,
            height=32,
            fg_color=self.primary_color_hex,
            hover_color=self.primary_color_hex,
            text_color="#000000",
            corner_radius=6,
            command=self._pick_color,
        )
        self.color_btn.grid(row=1, column=1, sticky="w", pady=(8, 0))

        # ── Background box row ──
        self.bg_box_var = ctk.BooleanVar(value=False)
        self.bg_check = ctk.CTkCheckBox(
            style_grid,
            text="Background box",
            variable=self.bg_box_var,
            font=ctk.CTkFont(size=13),
        )
        self.bg_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def _build_generate_button(self):
        self.generate_btn = ctk.CTkButton(
            self.root,
            text="Generate Subtitles",
            command=self.start_generation,
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            state="disabled",
        )
        self.generate_btn.pack(fill="x", padx=20, pady=(12, 8))

    def _build_progress_section(self):
        progress_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(4, 0))

        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=14)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        status_row = ctk.CTkFrame(self.root, fg_color="transparent")
        status_row.pack(fill="x", padx=20, pady=(6, 0))

        self.status_label = ctk.CTkLabel(
            status_row,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        self.status_label.pack(side="left")

        self.progress_label = ctk.CTkLabel(
            status_row,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        self.progress_label.pack(side="left", padx=(8, 0))

        self.stop_btn = ctk.CTkButton(
            status_row,
            text="Stop",
            command=self.stop_generation,
            width=70,
            height=28,
            fg_color="#b02a2a",
            hover_color="#cc3333",
            state="disabled",
        )
        self.stop_btn.pack(side="right")

    def _build_log_section(self):
        log_header = ctk.CTkFrame(self.root, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(10, 4))

        ctk.CTkLabel(
            log_header,
            text="Logs",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w")

        self.log_text = ctk.CTkTextbox(
            self.root,
            height=130,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#1a1a2e",
            text_color="#c8c8d0",
            corner_radius=10,
            state="disabled",
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    # ── Stdout Redirect ─────────────────────────────────────────────

    def write(self, text):
        self.original_stdout.write(text)
        self.root.after(0, self._append_log, text)

    def flush(self):
        self.original_stdout.flush()

    def _append_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ── Progress ─────────────────────────────────────────────────────

    def _on_progress(self, value, status_text=None):
        self.root.after(0, self._set_progress, value, status_text)

    def _set_progress(self, value, status_text):
        self.progress_bar.set(value / 100.0)
        self.progress_label.configure(text=f"{int(value)}%")
        if status_text:
            self.status_label.configure(text=status_text)

    # ── Event Handlers ───────────────────────────────────────────────

    def _validate_options(self):
        if self.video_path and (self.srt_var.get() or self.burn_var.get()):
            self.generate_btn.configure(state="normal")
        else:
            self.generate_btn.configure(state="disabled")

    def _pick_color(self):
        result = askcolor(color=self.primary_color_hex, title="Choose Subtitle Color")
        if result and result[1]:
            self.primary_color_hex = result[1].upper()
            r = int(self.primary_color_hex[1:3], 16)
            g = int(self.primary_color_hex[3:5], 16)
            b = int(self.primary_color_hex[5:7], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = "#000000" if brightness > 128 else "#FFFFFF"
            self.color_btn.configure(
                fg_color=self.primary_color_hex,
                hover_color=self.primary_color_hex,
                text=self.primary_color_hex,
                text_color=text_color,
            )

    @staticmethod
    def _hex_to_ass(hex_color):
        """Convert #RRGGBB to ASS &H00BBGGRR format used by FFmpeg."""
        h = hex_color.lstrip("#")
        r, g, b = h[0:2], h[2:4], h[4:6]
        return f"&H00{b}{g}{r}".upper()

    def select_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video Files", SUPPORTED_VIDEO_FORMATS),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.video_path = file_path
            self.video_entry.configure(state="normal")
            self.video_var.set(os.path.basename(file_path))
            self.video_entry.configure(state="disabled")
            self._validate_options()

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.output_entry.configure(state="normal")
            self.output_var.set(folder)
            self.output_entry.configure(state="disabled")

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
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Stopping...")

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
                do_burn=do_burn,
                subtitle_font=self.font_var.get() or None,
                primary_color=self._hex_to_ass(self.primary_color_hex),
                background_box=self.bg_box_var.get(),
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
        stop_state = "normal" if locked else "disabled"

        self.generate_btn.configure(state=state)
        self.select_btn.configure(state=state)
        self.output_btn.configure(state=state)
        self.srt_check.configure(state=state)
        self.burn_check.configure(state=state)
        self.model_combo.configure(state=state)
        self.lang_combo.configure(state=state)
        self.font_combo.configure(state=state)
        self.color_btn.configure(state=state)
        self.bg_check.configure(state=state)
        self.stop_btn.configure(state=stop_state)

        if locked:
            self.progress_bar.set(0)
            self.progress_label.configure(text="0%")
            self.status_label.configure(text="Processing video... Please wait")

    # ── Completion Callbacks ─────────────────────────────────────────

    def _on_success(self, srt_path, output_video_path, language):
        self._set_controls_locked(False)
        self.status_label.configure(text=f"Done! Detected language: {language}")

        msg_parts = []
        if srt_path:
            msg_parts.append(f"SRT file:\n{srt_path}")
        if output_video_path:
            msg_parts.append(f"Video with subtitles:\n{output_video_path}")
        messagebox.showinfo("Success", "\n\n".join(msg_parts))

    def _on_stopped(self):
        self._set_controls_locked(False)
        self.status_label.configure(text="Stopped by user.")

    def _on_error(self, error_msg):
        self._set_controls_locked(False)
        messagebox.showerror("Error", error_msg)
