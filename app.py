import customtkinter as ctk
from gui import SubtitleApp

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = SubtitleApp(root)
    root.mainloop()
