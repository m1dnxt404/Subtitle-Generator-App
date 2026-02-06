import pysrt


def build_srt(segments, srt_path, progress_callback=None, stop_check=None):
    """Build and save an SRT subtitle file from transcription segments."""
    if progress_callback:
        progress_callback(70, "Building subtitle data...")

    subs = pysrt.SubRipFile()
    total = len(segments)
    print(f"Processing segments... ({total} segments)")

    for i, segment in enumerate(segments):
        if stop_check and stop_check():
            raise InterruptedError("Process stopped by user.")
        subs.append(
            pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(seconds=segment["start"]),
                end=pysrt.SubRipTime(seconds=segment["end"]),
                text=segment["text"].strip()
            )
        )
        if progress_callback:
            progress_callback(70 + (i + 1) / total * 10)

    subs.save(srt_path, encoding="utf-8")

    if progress_callback:
        progress_callback(80)
    if stop_check and stop_check():
        raise InterruptedError("Process stopped by user.")
