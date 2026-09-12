import os

# ============================================================
# CUDA DLL - musi być ustawione PRZED importem faster_whisper
# ============================================================

CUDA_PATH = (
    r"C:\Users\marci\AppData\Local\Python\pythoncore-3.14-64"
    r"\Lib\site-packages\nvidia"
)

CUBLAS_PATH = os.path.join(CUDA_PATH, "cublas", "bin")
CUDNN_PATH = os.path.join(CUDA_PATH, "cudnn", "bin")

if os.path.exists(CUBLAS_PATH):
    os.add_dll_directory(CUBLAS_PATH)

if os.path.exists(CUDNN_PATH):
    os.add_dll_directory(CUDNN_PATH)

os.environ["PATH"] = (
    CUBLAS_PATH
    + os.pathsep
    + CUDNN_PATH
    + os.pathsep
    + os.environ["PATH"]
)

# ============================================================
# Imports
# ============================================================

import queue

import numpy as np
from scipy.signal import resample
from faster_whisper import WhisperModel

import config


class Transcriber:
    def __init__(self, audio_queue, text_queue):
        self.audio_queue = audio_queue
        self.text_queue = text_queue

        print("Ładowanie Whisper...")

        self.model = WhisperModel(
            config.MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )

        print(
            f"Whisper gotowy: "
            f"{config.MODEL_SIZE} | "
            f"{config.WHISPER_DEVICE} | "
            f"{config.WHISPER_COMPUTE_TYPE}"
        )

    def warmup(self):
        """
        Krótki test modelu przed rozpoczęciem pracy.
        """
        print("Whisper warmup...")

        dummy_audio = np.zeros(
            config.WHISPER_SAMPLE_RATE,
            dtype=np.float32,
        )

        segments, _ = self.model.transcribe(
            dummy_audio,
            language=config.WHISPER_LANGUAGE,
            beam_size=1,
            vad_filter=False,
        )

        # Wymuszenie wykonania generatora
        list(segments)

        print("Whisper warmup OK")

    def _prepare_audio(self, audio):
        """
        Przygotowuje audio z 48 kHz do 16 kHz,
        którego oczekuje Whisper.
        """

        audio = np.asarray(audio, dtype=np.float32)

        # Jeżeli audio jest stereo:
        # [lewy, prawy] -> mono
        if audio.ndim == 2:
            audio = np.mean(audio, axis=1)

        # Normalizacja zabezpieczająca
        max_value = np.max(np.abs(audio))

        if max_value > 1.0:
            audio = audio / max_value

        # 48 kHz -> 16 kHz
        if config.SAMPLE_RATE != config.WHISPER_SAMPLE_RATE:
            new_length = int(
                len(audio)
                * config.WHISPER_SAMPLE_RATE
                / config.SAMPLE_RATE
            )

            audio = resample(
                audio,
                new_length,
            )

        return audio.astype(np.float32)

    def transcribe_audio(self, audio):
        """
        Transkrybuje pojedynczą wypowiedź.
        """

        audio = self._prepare_audio(audio)

        if len(audio) == 0:
            return ""

        try:
            segments, info = self.model.transcribe(
                audio,
                language=config.WHISPER_LANGUAGE,
                beam_size=5,
                vad_filter=False,
                condition_on_previous_text=False,
            )

            text_parts = []

            for segment in segments:
                text = segment.text.strip()

                if text:
                    text_parts.append(text)

            return " ".join(text_parts).strip()

        except Exception as e:
            print(f"[WHISPER ERROR] {e}")
            return ""

    def run(self):
        """
        Główna pętla transkrypcji.

        Pobiera całe wypowiedzi z audio_queue
        i przekazuje tekst do text_queue.
        """

        print("Transcriber uruchomiony.")

        while True:
            try:
                audio = self.audio_queue.get()

                if audio is None:
                    break

                text = self.transcribe_audio(audio)

                if text:
                    print(f"EN: {text}")
                    self.text_queue.put(text)

            except Exception as e:
                print(f"[TRANSCRIBER ERROR] {e}")

            finally:
                self.audio_queue.task_done()

        print("Transcriber zatrzymany.")

    def start(self):
        """
        Uruchamia transcriber w osobnym wątku.
        """

        import threading

        thread = threading.Thread(
            target=self.run,
            daemon=True,
        )

        thread.start()

        return thread