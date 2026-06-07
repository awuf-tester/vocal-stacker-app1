import numpy as np
import librosa


class VocalThickener:
    def __init__(self):
        pass

    def apply_thickening(self, audio: np.ndarray, sr: int, intensity: float = 0.5, width: float = 0.5, variation: float = 0.3):
        if audio.ndim == 1:
            mono = audio
        else:
            mono = np.mean(audio, axis=1)

        offset_ms = 10 + (20 * intensity)
        pitch_shift = 0.1 + (0.9 * variation)
        delay_samples = int(sr * offset_ms / 1000.0)

        doubled = librosa.effects.pitch_shift(mono, sr, n_steps=pitch_shift * intensity)
        stretched = librosa.effects.time_stretch(doubled, rate=1.0 - variation * 0.08)
        if stretched.shape[0] < mono.shape[0]:
            stretched = np.pad(stretched, (0, mono.shape[0] - stretched.shape[0]))
        else:
            stretched = stretched[: mono.shape[0]]

        left = mono + np.pad(stretched * width, (delay_samples, 0), mode="constant")[: mono.shape[0]]
        right = mono + np.pad(stretched * width, (0, delay_samples), mode="constant")[: mono.shape[0]]

        stereo = np.vstack((left, right)).T
        peak = np.max(np.abs(stereo))
        if peak > 1.0:
            stereo = stereo / peak
        return stereo
