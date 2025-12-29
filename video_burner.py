from tkinter import filedialog
from config import VIDEO_TYPES
import os
import subprocess
import os
from config import SUBTITLE_STYLE

def burn_subtitles(video_path, srt_path):
    output_video = os.path.splitext(video_path)[0] + "_with_subs.mp4"

    style = (
        f"FontName={SUBTITLE_STYLE['font']},"
        f"FontSize={SUBTITLE_STYLE['font_size']},"
        f"PrimaryColour={SUBTITLE_STYLE['primary_color']},"
        f"OutlineColour={SUBTITLE_STYLE['outline_color']},"
        f"Outline={SUBTITLE_STYLE['outline']},"
        f"Shadow={SUBTITLE_STYLE['shadow']},"
        f"Alignment={SUBTITLE_STYLE['alignment']},"
        f"MarginV={SUBTITLE_STYLE['margin_v']}"
    )

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        output_video
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output_video
