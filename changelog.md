# Changelog

## [2026-02-06] - UI Enhancements in subtitle_gui.py

### Added

- Model size selector dropdown (tiny, base, small, medium, large) with parameter count and speed info
- Output folder selector button to choose where the SRT file is saved (defaults to same folder as video)
- Log container at the bottom with dark-themed text area and scrollbar — redirects all `print()` output to the GUI
- Stop Process button (red, right-aligned above logs) to cancel generation mid-process with graceful cleanup
- Determinate progress bar with percentage label — tracks each phase (audio extraction 0-10%, model loading 10-25%, transcription 25-80%, subtitle writing 80-100%)

### Changed

- Rearranged video file and output folder selectors to horizontal layout (button left, result right)
- Replaced result labels with readonly `Entry` widgets for a text container appearance
- Removed `tqdm` dependency — progress is now handled by the GUI progress bar

---

## [2026-02-05] - Bug Fixes in subtitle_gui.py

### Fixed

- Removed bogus `from unittest import result` import that shadowed the transcription result variable
- Changed `tk.Progressbar` to `ttk.Progressbar` — `Progressbar` does not exist in `tkinter`, only in `tkinter.ttk`
- Fixed `model.transcribe()` return handling — was incorrectly unpacking into `(segments, info)` tuple (faster-whisper API) instead of assigning to a single `result` dict (OpenAI whisper API)
- Fixed `result["segments"]` reference which previously pointed to the `unittest.result` module instead of the transcription output
- Added missing `subs.save(srt_path, encoding="utf-8")` call — SRT file was being built in memory but never written to disk
- Added missing `os.remove(audio_path)` to clean up the temporary `temp_audio.wav` file after processing
- Changed `info.language` to `result["language"]` to use correct dict access matching the OpenAI whisper API
