import numpy as np
import librosa


class VocalAligner:
    def __init__(self):
        self.reference = None

    @staticmethod
    def _envelope(signal: np.ndarray, sr: int):
        envelope = np.abs(signal)
        hop = max(1, sr // 200)
        envelope = np.convolve(envelope, np.ones(hop) / hop, mode="same")
        return envelope

    def align(self, reference: np.ndarray, target: np.ndarray, sr: int):
        if reference.size == 0 or target.size == 0:
            return target

        ref_env = self._envelope(reference, sr)
        tar_env = self._envelope(target, sr)
        ref_env = librosa.util.normalize(ref_env)
        tar_env = librosa.util.normalize(tar_env)

        correlation = np.correlate(tar_env, ref_env, mode="full")
        delay = correlation.argmax() - (len(ref_env) - 1)

        if delay > 0:
            aligned = np.concatenate((np.zeros(delay), target))
        else:
            aligned = target[-delay:]
        return aligned

    def align_tracks(self, tracks, sr: int):
        if not tracks:
            return []
        reference = tracks[0]
        aligned_tracks = [reference]
        for track in tracks[1:]:
            aligned = self.align(reference, track, sr)
            aligned_tracks.append(aligned)
        return aligned_tracks
