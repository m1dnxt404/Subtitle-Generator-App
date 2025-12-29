from tkinter import filedialog
from config import VIDEO_TYPES
import os

import subprocess
import os

def burn_subtitles(video_path, srt_path):
    output_video = os.path.splitext(video_path)[0] + "_with_subs.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        output_video
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output_video
