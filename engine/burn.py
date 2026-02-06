import subprocess


def burn_subtitles(video_path, srt_path, output_video_path,
                   progress_callback=None, stop_check=None):
    """Burn an SRT subtitle file into a video using ffmpeg."""
    if progress_callback:
        progress_callback(80, "Burning subtitles into video...")
    print("Burning subtitles into video (ffmpeg)...")

    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles='{srt_escaped}'",
        "-c:a", "copy",
        output_video_path
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    for line in process.stdout:
        if stop_check and stop_check():
            process.kill()
            raise InterruptedError("Process stopped by user.")
        line = line.strip()
        if line.startswith("frame="):
            print(line)
    process.wait()

    if process.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed to burn subtitles. "
            "Make sure ffmpeg is installed and in PATH."
        )

    print("Subtitles burned successfully.")
    if progress_callback:
        progress_callback(95)
