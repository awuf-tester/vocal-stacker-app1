import os
import customtkinter as ctk
from tkinter import filedialog


class SeparatorPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.selected_file = None
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text="Stem Separation", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        self.open_button = ctk.CTkButton(self, text="Select Source Track", command=self.choose_file)
        self.open_button.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

        self.stems_var = ctk.StringVar(value="vocals,drums,bass,other")
        self.stems_entry = ctk.CTkEntry(self, width=520, textvariable=self.stems_var)
        self.stems_entry.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 12))

        self.extract_button = ctk.CTkButton(self, text="Extract Stems", command=self.extract_stems)
        self.extract_button.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 12))

        self.progress_label = ctk.CTkLabel(self, text="No stem extraction started.")
        self.progress_label.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 12))

    def refresh(self):
        self.progress_label.configure(text="Ready for stem separation.")

    def choose_file(self):
        filepath = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])
        if filepath:
            self.selected_file = filepath
            self.progress_label.configure(text=f"Selected: {os.path.basename(filepath)}")

    def _progress_callback(self, value):
        self.progress_label.configure(text=f"Stem separation progress: {value:.0f}%")

    def _finished_callback(self, result, error):
        if error:
            self.progress_label.configure(text=f"Error: {error}")
        else:
            self.progress_label.configure(text=f"Extraction finished. Files saved to {result}")
            if isinstance(result, dict):
                self.progress_label.configure(text="Stem extraction completed.")

    def extract_stems(self):
        if not self.selected_file:
            self.progress_label.configure(text="Please select a source file first.")
            return
        stems = [stem.strip() for stem in self.stems_var.get().split(",") if stem.strip()]
        output_dir = os.path.join(os.getcwd(), "exports", "stems")
        self.progress_label.configure(text="Starting stem separation...")
        self.app.separator.separate_in_thread(
            self.selected_file,
            output_dir,
            stems,
            self._progress_callback,
            self._finished_callback,
        )
