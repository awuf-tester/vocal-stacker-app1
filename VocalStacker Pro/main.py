import os
import threading
import traceback
import numpy as np
import simpleaudio as sa
import customtkinter as ctk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from audio.stack import VocalStackEngine
from audio.align import VocalAligner
from audio.thickener import VocalThickener
from audio.cleaner import VocalCleaner
from audio.effects import EffectsProcessor
from audio.harmonies import HarmonyGenerator
from audio.exporter import Exporter
from ai.pitch_corrector import PitchCorrector
from ai.separator import DemucsSeparator
from ui.dashboard import DashboardPage
from ui.stack_page import StackPage
from ui.cleaner_page import CleanerPage
from ui.pitch_page import PitchPage
from ui.harmony_page import HarmonyPage
from ui.separator_page import SeparatorPage
from ui.export_page import ExportPage
from ui.settings_page import SettingsPage

APP_TITLE = "VocalStacker Pro"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 760


class VocalStackerProApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1100, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.project_name = "Untitled Project"
        self.audio_engine = VocalStackEngine()
        self.aligner = VocalAligner()
        self.thickener = VocalThickener()
        self.cleaner = VocalCleaner()
        self.effects = EffectsProcessor()
        self.harmony = HarmonyGenerator()
        self.pitch_corrector = PitchCorrector()
        self.separator = DemucsSeparator()
        self.exporter = Exporter()
        self.current_track = None
        self.playback_thread = None
        self.player = None
        self.playback_position = 0
        self.volume = 0.8
        self.recent_exports = []

        self.create_ui()
        self.create_pages()
        self.show_page("Dashboard")

    def create_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=(12, 6), pady=12)
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo = ctk.CTkLabel(self.sidebar, text=APP_TITLE, font=ctk.CTkFont(size=20, weight="bold"))
        self.logo.grid(row=0, column=0, pady=(16, 24))

        nav_items = [
            ("Dashboard", self.show_page),
            ("Vocal Stacking", self.show_page),
            ("Vocal Cleaner", self.show_page),
            ("Pitch Correction", self.show_page),
            ("Harmony Generator", self.show_page),
            ("Stem Separation", self.show_page),
            ("Export", self.show_page),
            ("Settings", self.show_page),
        ]

        for idx, (label, callback) in enumerate(nav_items, start=1):
            button = ctk.CTkButton(self.sidebar, text=label, command=lambda name=label: callback(name))
            button.grid(row=idx, column=0, sticky="ew", padx=12, pady=4)

        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w", height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="we", padx=12, pady=(0, 12))

    def create_pages(self):
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=1, sticky="nswe", padx=(6, 12), pady=12)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages = {
            "Dashboard": DashboardPage(container, self),
            "Vocal Stacking": StackPage(container, self),
            "Vocal Cleaner": CleanerPage(container, self),
            "Pitch Correction": PitchPage(container, self),
            "Harmony Generator": HarmonyPage(container, self),
            "Stem Separation": SeparatorPage(container, self),
            "Export": ExportPage(container, self),
            "Settings": SettingsPage(container, self),
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nswe")

    def show_page(self, page_name):
        page = self.pages.get(page_name)
        if page:
            page.tkraise()
            self.status_bar.configure(text=f"Viewing {page_name}")
            if hasattr(page, "refresh"):
                page.refresh()

    def set_status(self, message):
        self.status_bar.configure(text=message)

    def import_audio_files(self):
        try:
            filepaths = filedialog.askopenfilenames(
                title="Import Vocal Tracks",
                filetypes=[("Audio Files", "*.mp3 *.wav *.flac")],
            )
            if not filepaths:
                return
            for path in filepaths:
                self.audio_engine.add_track(path)
            self.set_status(f"Imported {len(filepaths)} tracks")
            self.pages["Dashboard"].refresh()
            self.pages["Vocal Stacking"].refresh()
        except Exception as exc:
            traceback.print_exc()
            messagebox.showerror("Import Error", str(exc))
            self.set_status("Failed to import audio")

    def get_project_summary(self):
        return {
            "name": self.project_name,
            "track_count": len(self.audio_engine.tracks),
            "recent_exports": self.recent_exports[-5:],
        }

    def add_recent_export(self, path):
        self.recent_exports.append(path)
        self.pages["Dashboard"].refresh()

    def _prepare_audio_buffer(self, audio, sr):
        if audio.ndim == 1:
            audio = np.vstack((audio, audio)).T
        audio = audio * self.volume
        audio = np.clip(audio, -1.0, 1.0)
        int_data = (audio * 32767).astype(np.int16)
        return int_data.tobytes(), sr, audio.shape[1]

    def play_audio(self, start_time: float = 0.0):
        if not self.current_track:
            self.set_status("No audio selected for playback.")
            return
        audio, sr = self.current_track
        if audio.ndim == 2:
            audio = audio[int(start_time * sr) :, :]
        else:
            audio = audio[int(start_time * sr) :]
        buffer_data, sample_rate, channels = self._prepare_audio_buffer(audio, sr)
        try:
            self.stop_audio()
            self.player = sa.play_buffer(buffer_data, channels, 2, sample_rate)
            self.playback_position = start_time
            self.set_status("Playing audio preview.")
        except Exception as exc:
            self.set_status(f"Playback error: {exc}")

    def stop_audio(self):
        if self.player and self.player.is_playing():
            self.player.stop()
            self.set_status("Playback stopped.")
        self.player = None

    def pause_audio(self):
        self.stop_audio()
        self.set_status("Playback paused.")

    def seek_audio(self, position: float):
        if not self.current_track:
            return
        self.stop_audio()
        self.play_audio(start_time=position)


if __name__ == "__main__":
    app = VocalStackerProApp()
    app.mainloop()
