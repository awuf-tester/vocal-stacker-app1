import customtkinter as ctk


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        self.theme_var = ctk.StringVar(value="dark")
        self.color_var = ctk.StringVar(value="dark-blue")

        ctk.CTkLabel(self, text="Appearance Mode").grid(row=1, column=0, sticky="w", padx=20)
        ctk.CTkOptionMenu(self, values=["dark", "light"], variable=self.theme_var, command=self.update_theme).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 12))

        ctk.CTkLabel(self, text="Color Theme").grid(row=3, column=0, sticky="w", padx=20)
        ctk.CTkOptionMenu(self, values=["blue", "dark-blue", "green", "dark-green", "purple"], variable=self.color_var, command=self.update_theme).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 12))

        self.status_label = ctk.CTkLabel(self, text="Change UI settings and performance options.")
        self.status_label.grid(row=5, column=0, sticky="w", padx=20, pady=(0, 12))

    def refresh(self):
        self.status_label.configure(text="Settings are ready to adjust.")

    def update_theme(self, _=None):
        ctk.set_appearance_mode(self.theme_var.get())
        ctk.set_default_color_theme(self.color_var.get())
        self.status_label.configure(text=f"Theme updated: {self.theme_var.get()}, {self.color_var.get()}")
