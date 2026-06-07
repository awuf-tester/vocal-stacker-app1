import customtkinter as ctk


class CleanerPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text="Vocal Cleaner", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        self.preset = ctk.StringVar(value="Studio Vocal")
        self.preset_menu = ctk.CTkOptionMenu(self, values=list(self.app.cleaner.PRESETS.keys()), variable=self.preset)
        self.preset_menu.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

        self.process_button = ctk.CTkButton(self, text="Process Selected Mix", command=self.process_clean)
        self.process_button.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 10))

        self.status_label = ctk.CTkLabel(self, text="Select a preset and process the vocal mix.")
        self.status_label.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 12))

    def refresh(self):
        self.status_label.configure(text="Ready to clean vocals.")

    def process_clean(self):
        if not self.app.current_track:
            self.status_label.configure(text="No mix preview available. Create one from Vocal Stacking.")
            return
        audio, sr = self.app.current_track
        preset_name = self.preset.get()
        cleaned = self.app.cleaner.process(audio[:, 0] if audio.ndim == 2 else audio, sr, preset_name)
        self.app.current_track = (cleaned if cleaned.ndim > 1 else cleaned[:, None] if cleaned.ndim == 1 else cleaned, sr)
        self.status_label.configure(text=f"Applied {preset_name} preset.")
