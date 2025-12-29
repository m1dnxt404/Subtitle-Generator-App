from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
import pysrt
import os
from config import MODEL_SIZE
from progress import calculate_progress

def generate_subtitles(video_path, progress_callback):
    video = VideoFileClip(video_path)
    total_duration = video.duration

    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path, logger=None)

    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, task="translate", beam_size=5)

    srt_path = os.path.splitext(video_path)[0] + ".srt"
    subs = pysrt.SubRipFile()

    index = 1
    for segment in segments:
        subs.append(
            pysrt.SubRipItem(
                index=index,
                start=pysrt.SubRipTime(seconds=segment.start),
                end=pysrt.SubRipTime(seconds=segment.end),
                text=segment.text.strip()
            )
        )
        index += 1
        progress_callback(calculate_progress(segment.end, total_duration))

    subs.save(srt_path, encoding="utf-8")
    os.remove(audio_path)

    return srt_path, info.language
