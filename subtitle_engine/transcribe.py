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


def transcribe(model, audio_path, target_language="en",
               progress_callback=None, stop_check=None):
    """Transcribe audio using a loaded Whisper model.

    Args:
        target_language: "original" keeps the spoken language as-is,
                         "en" uses Whisper's built-in translate-to-English,
                         any other code triggers transcribe (then translate later).
    """
    if target_language == "original":
        task = "transcribe"
        status = "Transcribing (original language)..."
    else:
        task = "translate"
        status = "Transcribing & translating to English..."

    if progress_callback:
        progress_callback(25, status)
    print(status)

    result = model.transcribe(
        audio_path,
        task=task,
        beam_size=5,
        verbose=True
    )

    if progress_callback:
        progress_callback(60)
    if stop_check and stop_check():
        raise InterruptedError("Process stopped by user.")
    return result
