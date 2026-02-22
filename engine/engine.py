import os

from .audio import extract_audio
from .transcribe import load_model, transcribe
from .translate import translate_segments
from .srt import build_srt
from .burn import burn_subtitles


class SubtitleEngine:
    """Orchestrates the full subtitle generation pipeline.

    Args:
        progress_callback: Called with (value, status_text) to report progress.
        stop_check: Called to check if the user requested a stop.
            Should return True if the process should stop.
    """

    def __init__(self, progress_callback=None, stop_check=None):
        self.progress_callback = progress_callback
        self.stop_check = stop_check

    def generate(self, video_path, model_size, srt_path,
                 target_language="en", output_video_path=None,
                 do_srt=True, do_burn=False, subtitle_font=None,
                 primary_color=None, background_box=False):
        """Run the full generation pipeline.

        Args:
            target_language: "en" for English (Whisper built-in),
                             "original" to keep spoken language,
                             any other lang code for post-translation.

        Returns:
            (srt_path or None, output_video_path or None, detected_language)
        """
        cb = self.progress_callback
        sc = self.stop_check
        audio_path = "temp_audio.wav"

        try:
            extract_audio(video_path, audio_path, cb, sc)
            model = load_model(model_size, cb, sc)
            result = transcribe(model, audio_path, target_language, cb, sc)

            # Post-translate if target is not English and not original
            if target_language not in ("en", "original"):
                translate_segments(result["segments"], target_language, cb, sc)

            build_srt(result["segments"], srt_path, cb, sc)

            if do_burn:
                burn_subtitles(
                    video_path, srt_path, output_video_path, cb, sc,
                    font_name=subtitle_font,
                    primary_color=primary_color,
                    background_box=background_box,
                )

            if not do_srt and do_burn:
                os.remove(srt_path)
                srt_path = None

            os.remove(audio_path)
            if cb:
                cb(100, "Complete!")

            return srt_path, output_video_path, result["language"]

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
