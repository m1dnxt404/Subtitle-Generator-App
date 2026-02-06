import os
import subprocess
import whisper
from moviepy import VideoFileClip
import pysrt


class SubtitleEngine:
    """Handles all subtitle generation logic, decoupled from the GUI.

    Args:
        progress_callback: Called with (value, status_text) to report progress.
        stop_check: Called to check if the user requested a stop.
            Should return True if the process should stop.
    """

    def __init__(self, progress_callback=None, stop_check=None):
        self.progress_callback = progress_callback
        self.stop_check = stop_check

    def _update_progress(self, value, status_text=None):
        if self.progress_callback:
            self.progress_callback(value, status_text)

    def _check_stop(self):
        if self.stop_check and self.stop_check():
            raise InterruptedError("Process stopped by user.")

    def extract_audio(self, video_path, audio_path):
        self._update_progress(0, "Extracting audio...")
        print("Extracting audio...")
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        self._update_progress(10)
        self._check_stop()

    def load_model(self, model_size):
        self._update_progress(10, "Loading Whisper model...")
        print("Loading Whisper model...")
        model = whisper.load_model(model_size)
        self._update_progress(25)
        self._check_stop()
        return model

    def transcribe(self, model, audio_path):
        self._update_progress(25, "Transcribing & translating...")
        print("Transcribing & translating...")
        result = model.transcribe(
            audio_path,
            task="translate",
            beam_size=5,
            verbose=True
        )
        self._update_progress(70)
        self._check_stop()
        return result

    def build_srt(self, segments, srt_path):
        self._update_progress(70, "Building subtitle data...")
        subs = pysrt.SubRipFile()
        total = len(segments)
        print(f"Processing segments... ({total} segments)")

        for i, segment in enumerate(segments):
            self._check_stop()
            subs.append(
                pysrt.SubRipItem(
                    index=i + 1,
                    start=pysrt.SubRipTime(seconds=segment["start"]),
                    end=pysrt.SubRipTime(seconds=segment["end"]),
                    text=segment["text"].strip()
                )
            )
            self._update_progress(70 + (i + 1) / total * 10)

        subs.save(srt_path, encoding="utf-8")
        self._update_progress(80)
        self._check_stop()

    def burn_subtitles(self, video_path, srt_path, output_video_path):
        self._update_progress(80, "Burning subtitles into video...")
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
            if self.stop_check and self.stop_check():
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
        self._update_progress(95)

    def generate(self, video_path, model_size, srt_path,
                 output_video_path=None, do_srt=True, do_burn=False):
        """Run the full generation pipeline.

        Returns:
            (srt_path or None, output_video_path or None, detected_language)
        """
        audio_path = "temp_audio.wav"

        try:
            self.extract_audio(video_path, audio_path)
            model = self.load_model(model_size)
            result = self.transcribe(model, audio_path)

            self.build_srt(result["segments"], srt_path)

            if do_burn:
                self.burn_subtitles(video_path, srt_path, output_video_path)

            if not do_srt and do_burn:
                os.remove(srt_path)
                srt_path = None

            os.remove(audio_path)
            self._update_progress(100, "Complete!")

            return srt_path, output_video_path, result["language"]

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
