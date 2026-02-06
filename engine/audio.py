from moviepy import VideoFileClip


def extract_audio(video_path, audio_path, progress_callback=None, stop_check=None):
    """Extract audio track from a video file to a WAV file."""
    if progress_callback:
        progress_callback(0, "Extracting audio...")
    print("Extracting audio...")

    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, logger=None)
    video.close()

    if progress_callback:
        progress_callback(10)
    if stop_check and stop_check():
        raise InterruptedError("Process stopped by user.")
