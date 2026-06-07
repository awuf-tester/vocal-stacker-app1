import numpy as np
import scipy.signal as signal


class EffectsProcessor:
    def __init__(self):
        pass

    def reverb(self, audio: np.ndarray, sr: int, decay=0.4, mix=0.25):
        length = int(sr * 0.3)
        impulse = np.logspace(0, -3, length)
        impulse = impulse * decay
        wet = signal.convolve(audio, impulse, mode="full")[: len(audio)]
        output = audio * (1 - mix) + wet * mix
        return self._normalize(output)

    def delay(self, audio: np.ndarray, sr: int, delay_ms=250, feedback=0.25, mix=0.2):
        delay_samples = int(sr * delay_ms / 1000)
        wet = np.zeros_like(audio)
        for i in range(delay_samples, len(audio)):
            wet[i] = audio[i - delay_samples] + feedback * wet[i - delay_samples]
        output = audio * (1 - mix) + wet * mix
        return self._normalize(output)

    def chorus(self, audio: np.ndarray, sr: int, depth=0.02, rate=1.2, mix=0.25):
        if audio.ndim == 1:
            audio = np.vstack((audio, audio)).T
        wet = np.zeros_like(audio)
        n = len(audio)
        for channel in range(2):
            for i in range(n):
                modulation = int((0.5 + 0.5 * np.sin(2 * np.pi * rate * i / sr)) * depth * sr)
                idx = min(n - 1, max(0, i - modulation))
                wet[i, channel] = audio[idx, channel]
        output = audio * (1 - mix) + wet * mix
        return self._normalize(output)

    def stereo_width(self, audio: np.ndarray, amount=0.5):
        if audio.ndim == 1:
            audio = np.vstack((audio, audio)).T
        mid = (audio[:, 0] + audio[:, 1]) / 2
        side = (audio[:, 0] - audio[:, 1]) / 2
        side *= 1 + amount
        left = mid + side
        right = mid - side
        stereo = np.vstack((left, right)).T
        return self._normalize(stereo)

    def compressor(self, audio: np.ndarray, threshold=0.5, ratio=4.0):
        return self._normalize(self._threshold_compress(audio, threshold, ratio))

    def limiter(self, audio: np.ndarray, ceiling=0.95):
        peak = np.max(np.abs(audio))
        if peak > ceiling:
            return audio * (ceiling / peak)
        return audio

    def _threshold_compress(self, audio: np.ndarray, threshold, ratio):
        compressed = np.copy(audio)
        mask = np.abs(audio) > threshold
        compressed[mask] = np.sign(audio[mask]) * (threshold + (np.abs(audio[mask]) - threshold) / ratio)
        return compressed

    def _normalize(self, audio: np.ndarray):
        peak = np.max(np.abs(audio))
        if peak > 1.0:
            return audio / peak
        return audio
