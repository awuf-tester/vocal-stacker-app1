import os
import threading

try:
    from demucs import pretrained
    from demucs.apply import apply_model
    from demucs.audio import AudioFile
except ImportError:
    pretrained = None
    apply_model = None
    AudioFile = None


class DemucsSeparator:
    def __init__(self):
        self.model = None

    def load_model(self, model_name: str = "mdx_extra"):
        if pretrained is None:
            raise ImportError("Demucs is required for stem separation")
        self.model = pretrained.get_model(model_name)
        return self.model

    def separate(self, filepath: str, output_dir: str, stems=["vocals", "drums", "bass", "other"], progress_callback=None):
        if pretrained is None or apply_model is None or AudioFile is None:
            raise RuntimeError("Demucs is not installed or unavailable")

        model = self.model or self.load_model()
        os.makedirs(output_dir, exist_ok=True)
        wav = AudioFile(filepath).read(streams=0)
        sources = apply_model(model, wav, shifts=1, split=True, progress=False)

        results = {}
        for idx, stem in enumerate(stems):
            if idx >= len(sources):
                continue
            stem_path = os.path.join(output_dir, f"{stem}.wav")
            AudioFile.save(stem_path, sources[idx], samplerate=model.samplerate)
            results[stem] = stem_path
            if progress_callback:
                progress_callback((idx + 1) / len(stems) * 100)
        return results

    def separate_in_thread(self, filepath, output_dir, stems, progress_callback, finished_callback):
        worker = threading.Thread(
            target=self._separate_worker,
            args=(filepath, output_dir, stems, progress_callback, finished_callback),
            daemon=True,
        )
        worker.start()
        return worker

    def _separate_worker(self, filepath, output_dir, stems, progress_callback, finished_callback):
        try:
            result = self.separate(filepath, output_dir, stems, progress_callback)
            if finished_callback:
                finished_callback(result, None)
        except Exception as exc:
            if finished_callback:
                finished_callback(None, exc)
