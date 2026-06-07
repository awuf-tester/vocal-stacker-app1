import customtkinter as ctk


class HarmonyPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text="Harmony Generator", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        self.mode_var = ctk.StringVar(value="High Harmony")
        self.mix_var = ctk.DoubleVar(value=0.35)

        ctk.CTkLabel(self, text="Harmony Type").grid(row=1, column=0, sticky="w", padx=20)
        ctk.CTkOptionMenu(self, values=list(self.app.harmony.INTERVALS.keys()), variable=self.mode_var).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 12))

        ctk.CTkLabel(self, text="Mix Amount").grid(row=3, column=0, sticky="w", padx=20)
        ctk.CTkSlider(self, from_=0.0, to=1.0, variable=self.mix_var, number_of_steps=100).grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 12))

        self.generate_button = ctk.CTkButton(self, text="Generate Harmony", command=self.generate_harmony)
        self.generate_button.grid(row=5, column=0, sticky="w", padx=20, pady=(0, 10))

        self.status_label = ctk.CTkLabel(self, text="Create a harmony vocal from the current mix.")
        self.status_label.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 12))

    def refresh(self):
        self.status_label.configure(text="Ready to generate harmony.")

    def generate_harmony(self):
        if not self.app.current_track:
            self.status_label.configure(text="No mix preview available.")
            return
        audio, sr = self.app.current_track
        harmony_audio = self.app.harmony.generate_harmony(
            audio[:, 0] if audio.ndim == 2 else audio,
            sr,
            mode=self.mode_var.get(),
            mix=self.mix_var.get(),
        )
        self.app.current_track = (harmony_audio, sr)
        self.status_label.configure(text=f"Generated {self.mode_var.get()}.")
