import customtkinter as ctk


class PitchPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text="Pitch Correction", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        self.strength_var = ctk.DoubleVar(value=0.6)
        self.scale_var = ctk.StringVar(value="Major")
        self.mode_var = ctk.StringVar(value="Natural")

        ctk.CTkLabel(self, text="Correction Strength").grid(row=1, column=0, sticky="w", padx=20)
        ctk.CTkSlider(self, from_=0.0, to=1.0, variable=self.strength_var, number_of_steps=100).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 12))

        ctk.CTkLabel(self, text="Target Scale").grid(row=3, column=0, sticky="w", padx=20)
        ctk.CTkOptionMenu(self, values=list(self.app.pitch_corrector.SCALES.keys()), variable=self.scale_var).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 12))

        ctk.CTkLabel(self, text="Mode").grid(row=5, column=0, sticky="w", padx=20)
        ctk.CTkOptionMenu(self, values=["Natural", "Strong"], variable=self.mode_var).grid(row=6, column=0, sticky="w", padx=20, pady=(0, 12))

        self.apply_button = ctk.CTkButton(self, text="Apply Pitch Correction", command=self.apply_correction)
        self.apply_button.grid(row=7, column=0, sticky="w", padx=20, pady=(0, 10))

        self.status_label = ctk.CTkLabel(self, text="Use pitch correction to smooth tuning errors.")
        self.status_label.grid(row=8, column=0, sticky="w", padx=20, pady=(0, 12))

    def refresh(self):
        self.status_label.configure(text="Ready to apply pitch correction.")

    def apply_correction(self):
        if not self.app.current_track:
            self.status_label.configure(text="No audio available to correct.")
            return
        audio, sr = self.app.current_track
        corrected = self.app.pitch_corrector.correct(
            audio[:, 0] if audio.ndim == 2 else audio,
            sr,
            strength=self.strength_var.get(),
            scale=self.scale_var.get(),
            mode=self.mode_var.get(),
        )
        corrected = corrected if corrected.ndim > 1 else corrected[:, None]
        self.app.current_track = (corrected, sr)
        self.status_label.configure(text="Pitch correction applied.")
