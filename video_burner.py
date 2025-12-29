from tkinter import filedialog
from config import VIDEO_TYPES
import os

def select_video(label, enable_button_callback):
    file_path = filedialog.askopenfilename(filetypes=VIDEO_TYPES)
    if file_path:
        label.config(text=os.path.basename(file_path), fg="black")
        enable_button_callback()
        return file_path
    else:
        label.config(text="No file selected", fg="red")
    return None