import customtkinter as ctk
import tkinter as tk
from functools import partial


class StackPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(self, text="Vocal Stacking", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.align_button = ctk.CTkButton(button_frame, text="Auto Align", command=self.auto_align)
        self.align_button.grid(row=0, column=0, padx=6, pady=4)
        self.mix_button = ctk.CTkButton(button_frame, text="Preview Mix", command=self.preview_mix)
        self.mix_button.grid(row=0, column=1, padx=6, pady=4)
        self.refresh_button = ctk.CTkButton(button_frame, text="Refresh", command=self.refresh)
        self.refresh_button.grid(row=0, column=2, padx=6, pady=4)

        self.track_frame = ctk.CTkScrollableFrame(self, width=900)
        self.track_frame.grid(row=2, column=0, sticky="nswe", padx=20, pady=(0, 20))
        self.track_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self, text="Ready to stack vocals.")
        self.status_label.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 20))

        self.refresh()

    def refresh(self):
        for widget in self.track_frame.winfo_children():
            widget.destroy()

        for idx, track in enumerate(self.app.audio_engine.tracks):
            row = ctk.CTkFrame(self.track_frame)
            row.grid(row=idx, column=0, sticky="ew", padx=12, pady=10)
            row.grid_columnconfigure(3, weight=1)

            label = ctk.CTkLabel(row, text=track.name)
            label.grid(row=0, column=0, sticky="w", padx=8)

            enabled = ctk.CTkCheckBox(row, text="Enabled", variable=ctk.BooleanVar(value=track.enabled), command=partial(self.toggle_enabled, idx))
            enabled.grid(row=0, column=1, padx=8)
            mute = ctk.CTkCheckBox(row, text="Mute", variable=ctk.BooleanVar(value=track.mute), command=partial(self.toggle_mute, idx))
            mute.grid(row=0, column=2, padx=8)
            solo = ctk.CTkCheckBox(row, text="Solo", variable=ctk.BooleanVar(value=track.solo), command=partial(self.toggle_solo, idx))
            solo.grid(row=0, column=3, padx=8)

            volume = ctk.CTkSlider(row, from_=0.0, to=2.0, number_of_steps=40, command=partial(self.set_volume, idx))
            volume.set(track.volume)
            volume.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 0))
            pan = ctk.CTkSlider(row, from_=-1.0, to=1.0, number_of_steps=40, command=partial(self.set_pan, idx))
            pan.set(track.pan)
            pan.grid(row=1, column=2, columnspan=2, sticky="ew", padx=8, pady=(8, 0))

    def toggle_enabled(self, idx):
        track = self.app.audio_engine.tracks[idx]
        self.app.audio_engine.set_track_state(idx, enabled=not track.enabled)
        self.app.set_status(f"Track {track.name} enabled={not track.enabled}")

    def toggle_mute(self, idx):
        track = self.app.audio_engine.tracks[idx]
        self.app.audio_engine.set_track_state(idx, mute=not track.mute)
        self.app.set_status(f"Track {track.name} mute={not track.mute}")

    def toggle_solo(self, idx):
        track = self.app.audio_engine.tracks[idx]
        self.app.audio_engine.set_track_state(idx, solo=not track.solo)
        self.app.set_status(f"Track {track.name} solo={not track.solo}")

    def set_volume(self, idx, value):
        self.app.audio_engine.set_track_state(idx, volume=value)

    def set_pan(self, idx, value):
        self.app.audio_engine.set_track_state(idx, pan=value)

    def auto_align(self):
        self.status_label.configure(text="Aligning tracks...")
        active_tracks = [track for track in self.app.audio_engine.tracks if track.enabled and not track.mute]
        if not active_tracks:
            self.status_label.configure(text="No tracks available for alignment.")
            return
        tracks = [track.mono for track in active_tracks]
        sr = active_tracks[0].sr
        aligned = self.app.aligner.align_tracks(tracks, sr)
        for track, aligned_audio in zip(active_tracks, aligned):
            track.mono = aligned_audio
        self.status_label.configure(text="Tracks aligned successfully.")

    def preview_mix(self):
        self.status_label.configure(text="Preparing mix preview...")
        mix, sr = self.app.audio_engine.mix()
        if mix.size == 0:
            self.status_label.configure(text="No active tracks to mix.")
            return
        self.app.current_track = (mix, sr)
        self.status_label.configure(text="Mix preview ready.")
