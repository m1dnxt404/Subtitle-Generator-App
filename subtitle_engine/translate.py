from deep_translator import GoogleTranslator


def translate_segments(segments, target_lang, progress_callback=None, stop_check=None):
    """Translate segment texts from English to the target language.

    Modifies segment dicts in-place, updating the 'text' field.
    Uses Google Translate via deep-translator (no API key needed).
    """
    if progress_callback:
        progress_callback(60, f"Translating to {target_lang}...")
    print(f"Translating segments to '{target_lang}'...")

    translator = GoogleTranslator(source="en", target=target_lang)
    total = len(segments)

    for i, segment in enumerate(segments):
        if stop_check and stop_check():
            raise InterruptedError("Process stopped by user.")
        segment["text"] = translator.translate(segment["text"].strip())
        if progress_callback:
            progress_callback(60 + (i + 1) / total * 10)

    print("Translation complete.")
