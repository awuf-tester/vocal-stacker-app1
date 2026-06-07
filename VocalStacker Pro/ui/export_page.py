import os
import customtkinter as ctk
from tkinter import filedialog


class ExportPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text="Export", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        self.format_var = ctk.StringVar(value="wav")
        self.preset_var = ctk.StringVar(value="Studio Quality")
        self.destination_var = ctk.StringVar(value=os.path.join(os.getcwd(), "exports"))

        ctk.CTkLabel(self, text="Export Format").grid(row=1, column=0, sticky="w", padx=20)
        ctk.CTkOptionMenu(self, values=["wav", "mp3", "flac"], variable=self.format_var).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 12))

        ctk.CTkLabel(self, text="Quality Preset").grid(row=3, column=0, sticky="w", padx=20)
        ctk.CTkOptionMenu(self, values=list(self.app.exporter.PRESSETS.keys()), variable=self.preset_var).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 12))

        dest_frame = ctk.CTkFrame(self)
        dest_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 12))
        dest_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(dest_frame, text="Destination").grid(row=0, column=0, sticky="w")
        ctk.CTkEntry(dest_frame, textvariable=self.destination_var).grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkButton(dest_frame, text="Browse", command=self.choose_destination).grid(row=0, column=2, padx=(8, 0))

        self.export_button = ctk.CTkButton(self, text="Export Current Track", command=self.export_current)
        self.export_button.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 10))

        self.status_label = ctk.CTkLabel(self, text="Ready to export processed audio.")
        self.status_label.grid(row=7, column=0, sticky="w", padx=20, pady=(0, 12))

    def refresh(self):
        self.status_label.configure(text="Ready to export audio.")

    def choose_destination(self):
        folder = filedialog.askdirectory(title="Select Export Folder")
        if folder:
            self.destination_var.set(folder)

    def export_current(self):
        if not self.app.current_track:
            self.status_label.configure(text="No audio available to export.")
            return
        audio, sr = self.app.current_track
        output_dir = self.destination_var.get()
        os.makedirs(output_dir, exist_ok=True)
        filename = f"VocalStackerPro_export.{self.format_var.get()}"
        output_path = os.path.join(output_dir, filename)
        try:
            result = self.app.exporter.export(audio, sr, output_path, format=self.format_var.get(), preset=self.preset_var.get())
            self.app.add_recent_export(result)
            self.status_label.configure(text=f"Exported file: {result}")
        except Exception as exc:
            self.status_label.configure(text=f"Export failed: {exc}")
