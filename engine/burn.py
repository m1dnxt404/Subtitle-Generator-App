import subprocess


def burn_subtitles(video_path, srt_path, output_video_path,
                   progress_callback=None, stop_check=None,
                   font_name=None, primary_color=None, background_box=False):
    """Burn an SRT subtitle file into a video using ffmpeg."""
    if progress_callback:
        progress_callback(80, "Burning subtitles into video...")
    print("Burning subtitles into video (ffmpeg)...")

    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    style_parts = []
    if font_name:
        safe_font = font_name.replace("'", "").replace("\\", "")
        style_parts.append(f"FontName={safe_font}")
    if primary_color:
        style_parts.append(f"PrimaryColour={primary_color}")
    if background_box:
        style_parts.append("BorderStyle=3")
        style_parts.append("BackColour=&H80000000")

    vf_filter = f"subtitles='{srt_escaped}'"
    if style_parts:
        vf_filter += f":force_style='{','.join(style_parts)}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", vf_filter,
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
