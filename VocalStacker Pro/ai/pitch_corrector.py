import numpy as np
import librosa


class PitchCorrector:
    SCALES = {
        "Major": [0, 2, 4, 5, 7, 9, 11],
        "Minor": [0, 2, 3, 5, 7, 8, 10],
        "Chromatic": list(range(12)),
    }

    def __init__(self):
        pass

    def detect_pitch(self, audio: np.ndarray, sr: int):
        f0, voiced_flag, _ = librosa.pyin(audio, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr)
        return f0

    def correct(self, audio: np.ndarray, sr: int, strength: float = 0.6, scale: str = "Major", mode: str = "Natural"):
        if audio.ndim == 2:
            audio = np.mean(audio, axis=1)
        target_notes = self.SCALES.get(scale, self.SCALES["Major"])
        pitch = self.detect_pitch(audio, sr)
        if pitch is None or np.all(np.isnan(pitch)):
            return audio

        semitones = librosa.hz_to_midi(pitch)
        corrected = np.copy(audio)
        for i in range(0, len(audio), 1024):
            frame = audio[i : i + 1024]
            if frame.size == 0:
                continue
            n = pitch[i] if i < len(pitch) else np.nan
            if np.isnan(n):
                continue
            nearest = self._closest_scale_note(n, target_notes)
            shift = nearest - n
            shift *= strength if mode == "Strong" else strength * 0.6
            corrected[i : i + 1024] = librosa.effects.pitch_shift(frame, sr, n_steps=shift)

        if len(corrected) > len(audio):
            corrected = corrected[: len(audio)]
        return corrected

    def _closest_scale_note(self, midi_note: float, scale_intervals):
        root = int(np.floor(midi_note / 12)) * 12
        candidates = [root + interval for interval in scale_intervals] + [root + 12 + interval for interval in scale_intervals]
        distances = [abs(midi_note - candidate) for candidate in candidates]
        return candidates[int(np.argmin(distances))]
