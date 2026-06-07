import numpy as np
import librosa


class HarmonyGenerator:
    INTERVALS = {
        "High Harmony": 4,
        "Low Harmony": -3,
        "Octave Up": 12,
        "Octave Down": -12,
    }

    def generate_harmony(self, audio: np.ndarray, sr: int, mode: str = "High Harmony", mix: float = 0.35):
        semitone = self.INTERVALS.get(mode, 4)
        if audio.ndim == 2:
            base = np.mean(audio, axis=1)
        else:
            base = audio

        harmony = librosa.effects.pitch_shift(base, sr, n_steps=semitone)
        harmony = self._fit_length(harmony, len(base))
        stereo = np.vstack((base * (1 - mix), harmony * mix)).T
        peak = np.max(np.abs(stereo))
        if peak > 1.0:
            stereo = stereo / peak
        return stereo

    def _fit_length(self, audio: np.ndarray, target_len: int):
        if len(audio) < target_len:
            return np.pad(audio, (0, target_len - len(audio)))
        return audio[:target_len]
