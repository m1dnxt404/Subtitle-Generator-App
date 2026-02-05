# Changelog

## [2026-02-05] - Bug Fixes in subtitle_gui.py

### Fixed

- Removed bogus `from unittest import result` import that shadowed the transcription result variable
- Changed `tk.Progressbar` to `ttk.Progressbar` — `Progressbar` does not exist in `tkinter`, only in `tkinter.ttk`
- Fixed `model.transcribe()` return handling — was incorrectly unpacking into `(segments, info)` tuple (faster-whisper API) instead of assigning to a single `result` dict (OpenAI whisper API)
- Fixed `result["segments"]` reference which previously pointed to the `unittest.result` module instead of the transcription output
- Added missing `subs.save(srt_path, encoding="utf-8")` call — SRT file was being built in memory but never written to disk
- Added missing `os.remove(audio_path)` to clean up the temporary `temp_audio.wav` file after processing
- Changed `info.language` to `result["language"]` to use correct dict access matching the OpenAI whisper API
