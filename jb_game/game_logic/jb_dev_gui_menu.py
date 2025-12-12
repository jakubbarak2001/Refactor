import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import pygame  # <--- NEW: Import the audio engine


def resource_path(relative_path):
    """ Get absolute path to resource (Works for Dev & EXE) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class AnimatedGifLabel(tk.Label):
    """ Custom Label to display animated GIFs with Resizing """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.original_image = None
        self.frames = []
        self.frames_len = 0
        self.loc = 0
        self.delay = 100

    def load(self, path, width, height):
        self.original_image = Image.open(path)
        self.frames = []

        try:
            # Modern Pillow Resampling
            resample_mode = Image.Resampling.LANCZOS

            i = 0
            while True:
                self.original_image.seek(i)
                frame = self.original_image.copy()
                frame = frame.resize((width, height), resample_mode)
                self.frames.append(ImageTk.PhotoImage(frame))
                i += 1
        except EOFError:
            pass

        self.frames_len = len(self.frames)
        self.loc = 0
        self.delay = self.original_image.info.get("duration", 100)

        if self.frames_len > 0:
            self.next_frame()

    def next_frame(self):
        if self.frames:
            self.config(image=self.frames[self.loc])
            self.loc += 1
            if self.loc >= self.frames_len:
                self.loc = 0
            self.after(self.delay, self.next_frame)


def show_startup_menu():
    # --- CONFIG ---
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    GIF_NAME = "gun_loop.gif"
    MUSIC_NAME = "menu_theme.mp3"  # <--- YOUR MUSIC FILE
    # --------------

    root = tk.Tk()
    root.title("JB: THE DARKEST SHIFT")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False)
    root.configure(bg="#000000")

    # --- 1. START MUSIC ---
    music_path = resource_path(MUSIC_NAME)
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # -1 means Loop Forever
        pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
    except Exception as e:
        print(f"Music Error: {e}")  # Won't crash game, just no sound

    # --- 2. LOAD GIF ---
    gif_path = resource_path(GIF_NAME)
    try:
        lbl_anim = AnimatedGifLabel(master=root, bg="#000000")
        lbl_anim.pack(expand=True, fill="both")
        lbl_anim.load(gif_path, WINDOW_WIDTH, WINDOW_HEIGHT)
    except Exception as e:
        err = tk.Label(root, text=f"ERROR: {e}", fg="red", bg="black")
        err.pack(pady=50)

    # --- 3. START BUTTON ---
    def on_play():
        # Stop music before destroying window
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
        root.destroy()

    start_btn = tk.Button(root,
                          text="> ENTER THE SHIFT",
                          font=("Impact", 28),
                          fg="#00FF00",
                          bg="black",
                          activeforeground="white",
                          activebackground="black",
                          bd=0,
                          command=on_play)

    start_btn.place(x=30, y=30)

    root.mainloop()