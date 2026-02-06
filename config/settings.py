# Model   | Parameters  | Relative Speed |
# --------|-------------|----------------|
# tiny    | 39M         | Fastest        |
# base    | 74M         | Fast           |
# small   | 244M        | Moderate       |
# medium  | 769M        | Slow           |
# large   | 1550M       | Slowest        |
MODEL_OPTIONS = {
    "tiny (39M - Fastest/least Accurate)": "tiny",
    "base (74M - Fast)": "base",
    "small (244M - Moderate)": "small",
    "medium (769M - Slow)": "medium",
    "large (1550M - Slowest/Most Accurate)": "large",
}

SUPPORTED_VIDEO_FORMATS = "*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.webm *.m4v *.mpg *.mpeg *.3gp *.ts"

LANGUAGE_OPTIONS = {
    "English": "en",
    "Original (No Translation)": "original",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Portuguese": "pt",
    "Italian": "it",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
    "Turkish": "tr",
    "Dutch": "nl",
    "Polish": "pl",
}

WINDOW_TITLE = "Video Subtitle Generator"
WINDOW_SIZE = "550x710"
