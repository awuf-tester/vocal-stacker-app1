import os
import numpy as np
import soundfile as sf
import librosa


class VocalTrack:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.name = os.path.basename(filepath)
        self.data, self.sr = sf.read(filepath, always_2d=True)
        self.mono = librosa.to_mono(self.data.T)
        self.duration = len(self.mono) / self.sr
        self.enabled = True
        self.volume = 1.0
        self.pan = 0.0
        self.mute = False
        self.solo = False

    @property
    def is_active(self):
        return self.enabled and not self.mute


class VocalStackEngine:
    def __init__(self):
        self.tracks = []

    def add_track(self, filepath: str):
        track = VocalTrack(filepath)
        self.tracks.append(track)
        return track

    def remove_track(self, index: int):
        if 0 <= index < len(self.tracks):
            del self.tracks[index]

    def set_track_state(self, index: int, enabled: bool = None, volume: float = None, pan: float = None, mute: bool = None, solo: bool = None):
        if 0 <= index < len(self.tracks):
            track = self.tracks[index]
            if enabled is not None:
                track.enabled = enabled
            if volume is not None:
                track.volume = max(0.0, min(2.0, volume))
            if pan is not None:
                track.pan = max(-1.0, min(1.0, pan))
            if mute is not None:
                track.mute = mute
            if solo is not None:
                track.solo = solo

    def get_active_tracks(self):
        if any(track.solo for track in self.tracks):
            return [t for t in self.tracks if t.solo and t.enabled and not t.mute]
        return [t for t in self.tracks if t.enabled and not t.mute]

    def mix(self):
        active = self.get_active_tracks()
        if not active:
            return np.zeros((0, 2), dtype=np.float32), 44100

        target_sr = max(track.sr for track in active)
        normalized = []
        for track in active:
            data = track.mono
            if track.sr != target_sr:
                data = librosa.resample(data, orig_sr=track.sr, target_sr=target_sr)
            volume = track.volume if not track.mute else 0.0

            pan = np.clip(track.pan, -1.0, 1.0)
            left_gain = np.sqrt(1.0 - pan) * volume
            right_gain = np.sqrt(1.0 + pan) * volume
            stereo = np.vstack((data * left_gain, data * right_gain)).T
            normalized.append(stereo)

        max_len = max(item.shape[0] for item in normalized)
        mix = np.zeros((max_len, 2), dtype=np.float32)
        for segment in normalized:
            mix[: segment.shape[0]] += segment

        peak = np.max(np.abs(mix))
        if peak > 1.0:
            mix = mix / peak

        return mix, target_sr

    def export_mix(self, filepath: str, format: str = "wav"):
        mix, sr = self.mix()
        if mix.size == 0:
            raise RuntimeError("No active tracks to export")
        sf.write(filepath, mix, sr, format=format)
        return filepath
