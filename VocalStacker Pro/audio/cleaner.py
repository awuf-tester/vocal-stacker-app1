import numpy as np
import librosa
import scipy.signal as signal


class VocalCleaner:
    PRESETS = {
        "Studio Vocal": {"noise_reduction": 0.18, "eq_gain": [1.1, 1.05, 1.0, 0.95], "compression": 0.15},
        "Podcast Voice": {"noise_reduction": 0.22, "eq_gain": [1.2, 1.1, 1.0, 0.9], "compression": 0.2},
        "Rap Vocal": {"noise_reduction": 0.2, "eq_gain": [1.1, 1.15, 1.05, 0.9], "compression": 0.35},
        "Soft Vocal": {"noise_reduction": 0.15, "eq_gain": [1.05, 1.0, 0.95, 0.9], "compression": 0.12},
        "Nasheed Vocal": {"noise_reduction": 0.18, "eq_gain": [1.0, 1.05, 1.05, 0.95], "compression": 0.18},
    }

    def noise_reduction(self, audio: np.ndarray, reduction: float):
        magnitude = np.abs(librosa.stft(audio, n_fft=2048, hop_length=512))
        threshold = np.percentile(magnitude, reduction * 100)
        audio_reduced = np.where(np.abs(audio) < threshold, audio * (1 - reduction), audio)
        return audio_reduced

    def apply_eq(self, audio: np.ndarray, sr: int, gains=None):
        if gains is None:
            gains = [1.0, 1.0, 1.0, 1.0]
        bands = [(80, 250), (250, 1000), (1000, 5000), (5000, 12000)]
        output = np.copy(audio)
        for gain, band in zip(gains, bands):
            b, a = signal.butter(2, [band[0] / (sr / 2), band[1] / (sr / 2)], btype="band")
            output += gain * signal.lfilter(b, a, audio)
        peak = np.max(np.abs(output))
        if peak > 1.0:
            output = output / peak
        return output

    def compress(self, audio: np.ndarray, threshold=0.5, ratio=2.5):
        compressed = np.copy(audio)
        mask = np.abs(audio) > threshold
        compressed[mask] = np.sign(audio[mask]) * (threshold + (np.abs(audio[mask]) - threshold) / ratio)
        return compressed

    def limiter(self, audio: np.ndarray, ceiling=0.98):
        peak = np.max(np.abs(audio))
        if peak > ceiling:
            audio = audio * (ceiling / peak)
        return audio

    def process(self, audio: np.ndarray, sr: int, preset_name: str = "Studio Vocal"):
        preset = self.PRESETS.get(preset_name, self.PRESETS["Studio Vocal"])
        clean = self.noise_reduction(audio, preset["noise_reduction"])
        clean = self.apply_eq(clean, sr, preset["eq_gain"])
        clean = self.compress(clean, threshold=0.25 + preset["compression"], ratio=2.5)
        clean = self.limiter(clean)
        return clean
