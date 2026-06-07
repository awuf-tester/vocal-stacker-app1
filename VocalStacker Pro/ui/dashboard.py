import os
import threading
import numpy as np
import soundfile as sf
import librosa
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        toolbar.grid_columnconfigure(2, weight=1)

        self.import_button = ctk.CTkButton(toolbar, text="Import Vocals", command=self.app.import_audio_files)
        self.import_button.grid(row=0, column=0, padx=6)
        self.refresh_button = ctk.CTkButton(toolbar, text="Refresh", command=self.refresh)
        self.refresh_button.grid(row=0, column=1, padx=6)
        self.play_button = ctk.CTkButton(toolbar, text="Play", command=self.play_audio)
        self.play_button.grid(row=0, column=2, padx=6)
        self.stop_button = ctk.CTkButton(toolbar, text="Stop", command=self.stop_audio)
        self.stop_button.grid(row=0, column=3, padx=6)

        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.grid(row=2, column=0, sticky="nswe", padx=20, pady=(0, 20))
        self.summary_frame.grid_columnconfigure(1, weight=1)

        self.project_label = ctk.CTkLabel(self.summary_frame, text="Project: Untitled Project")
        self.project_label.grid(row=0, column=0, sticky="w", padx=12, pady=12)
        self.track_count_label = ctk.CTkLabel(self.summary_frame, text="Tracks: 0")
        self.track_count_label.grid(row=0, column=1, sticky="e", padx=12, pady=12)

        self.file_list = ctk.CTkTextbox(self.summary_frame, width=720, height=180)
        self.file_list.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=12, pady=(0, 12))
        self.file_list.configure(state="disabled")

        self.export_list = ctk.CTkTextbox(self.summary_frame, width=720, height=120)
        self.export_list.grid(row=2, column=0, columnspan=2, sticky="nswe", padx=12, pady=(0, 12))
        self.export_list.configure(state="disabled")

        self.seek_var = ctk.DoubleVar(value=0.0)
        self.seek_slider = ctk.CTkSlider(self.summary_frame, from_=0.0, to=100.0, variable=self.seek_var, command=self.on_seek)
        self.seek_slider.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

        self.volume_var = ctk.DoubleVar(value=0.8)
        self.volume_slider = ctk.CTkSlider(self.summary_frame, from_=0.0, to=1.0, variable=self.volume_var, command=self.on_volume)
        self.volume_slider.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

        self.figure = plt.Figure(figsize=(10, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Waveform Preview")
        self.ax.axis("off")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.summary_frame)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, sticky="nswe", padx=12, pady=(0, 12))

    def play_audio(self):
        self.app.volume = self.volume_var.get()
        self.app.play_audio()

    def stop_audio(self):
        self.app.stop_audio()

    def on_seek(self, value):
        if self.app.current_track:
            duration = self.app.current_track[0].shape[0] / self.app.current_track[1]
            position = float(value) / 100.0 * duration
            self.app.seek_audio(position)

    def on_volume(self, value):
        self.app.volume = float(value)

    def refresh(self):
        summary = self.app.get_project_summary()
        self.project_label.configure(text=f"Project: {summary['name']}")
        self.track_count_label.configure(text=f"Tracks: {summary['track_count']}")

        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        for track in self.app.audio_engine.tracks:
            self.file_list.insert("end", f"{track.name} | {track.duration:.2f}s | {track.sr}Hz\n")
        self.file_list.configure(state="disabled")

        self.export_list.configure(state="normal")
        self.export_list.delete("1.0", "end")
        self.export_list.insert("end", "Recent Exports:\n")
        for path in summary["recent_exports"]:
            self.export_list.insert("end", f"{path}\n")
        self.export_list.configure(state="disabled")

        self.draw_waveform()

    def draw_waveform(self):
        self.ax.clear()
        self.ax.set_title("Waveform Preview")
        self.ax.axis("off")
        if self.app.audio_engine.tracks:
            track = self.app.audio_engine.tracks[0]
            try:
                data = track.mono
                times = np.linspace(0, track.duration, len(data))
                self.ax.plot(times, data, color="#00b4d8")
                self.ax.set_xlim(0, track.duration)
                self.ax.axis("off")
            except Exception:
                pass
        self.canvas.draw()
