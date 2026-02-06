import whisper


def load_model(model_size, progress_callback=None, stop_check=None):
    """Load a Whisper model by size name."""
    if progress_callback:
        progress_callback(10, "Loading Whisper model...")
    print("Loading Whisper model...")

    model = whisper.load_model(model_size)

    if progress_callback:
        progress_callback(25)
    if stop_check and stop_check():
        raise InterruptedError("Process stopped by user.")
    return model


def transcribe(model, audio_path, progress_callback=None, stop_check=None):
    """Transcribe and translate audio to English using a loaded Whisper model."""
    if progress_callback:
        progress_callback(25, "Transcribing & translating...")
    print("Transcribing & translating...")

    result = model.transcribe(
        audio_path,
        task="translate",
        beam_size=5,
        verbose=True
    )

    if progress_callback:
        progress_callback(70)
    if stop_check and stop_check():
        raise InterruptedError("Process stopped by user.")
    return result
