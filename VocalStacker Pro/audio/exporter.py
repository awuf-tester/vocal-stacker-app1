import os
import numpy as np
import soundfile as sf
from pydub import AudioSegment


class Exporter:
    PRESSETS = {
        "Studio Quality": {"bitrate": "320k", "format": "wav"},
        "High Quality": {"bitrate": "192k", "format": "mp3"},
        "Small File": {"bitrate": "128k", "format": "mp3"},
    }

    def export(self, audio: np.ndarray, sr: int, output_path: str, format: str = "wav", preset: str = "Studio Quality"):
        _, ext = os.path.splitext(output_path)
        ext = ext.lstrip(".").lower()
        format = ext if ext else format
        format = format.lower()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if format in ["wav", "flac"]:
            sf.write(output_path, audio, sr, format=format)
            return output_path

        if format == "mp3":
            try:
                segment = self._audiosegment_from_numpy(audio, sr)
                bitrate = self.PRESSETS.get(preset, {}).get("bitrate", "192k")
                segment.export(output_path, format="mp3", bitrate=bitrate)
                return output_path
            except Exception:
                fallback = os.path.splitext(output_path)[0] + ".wav"
                sf.write(fallback, audio, sr, format="wav")
                return fallback

        raise ValueError(f"Unsupported export format: {format}")

    def _audiosegment_from_numpy(self, audio: np.ndarray, sr: int):
        if audio.ndim == 1:
            audio = np.vstack((audio, audio)).T
        audio = np.clip(audio, -1.0, 1.0)
        int_data = (audio * 32767).astype(np.int16)
        raw = int_data.tobytes()
        return AudioSegment(
            data=raw,
            sample_width=2,
            frame_rate=sr,
            channels=2,
        )
