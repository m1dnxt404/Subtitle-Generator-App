# Model   | Parameters  | Relative Speed |
# --------|-------------|----------------|
# tiny    | 39M         | Fastest        |
# base    | 74M         | Fast           |
# small   | 244M        | Moderate       |
# medium  | 769M        | Slow           |
# large   | 1550M       | Slowest        |
MODEL_OPTIONS = {
    "tiny (39M - Fastest)": "tiny",
    "base (74M - Fast)": "base",
    "small (244M - Moderate)": "small",
    "medium (769M - Slow)": "medium",
    "large (1550M - Slowest)": "large",
}

SUPPORTED_VIDEO_FORMATS = "*.mp4 *.mkv *.avi *.mov *.flv"

WINDOW_TITLE = "Video Subtitle Generator (Translate to English)"
WINDOW_SIZE = "550x670"
