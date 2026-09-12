import queue

import numpy as np
import soundcard as sc
import webrtcvad

from config import (
    SAMPLE_RATE,
    FRAME_MS,
    SILENCE_MS,
    MIN_SPEECH_MS,
    MAX_UTTERANCE_SECONDS,
)


class AudioRecorder:

    def __init__(self, audio_queue: queue.Queue):

        self.audio_queue = audio_queue

        self.speaker = sc.default_speaker()

        print(
            f"[AUDIO] Speaker: "
            f"{self.speaker.name}"
        )

        self.loopback_mic = sc.get_microphone(
            id=str(self.speaker.name),
            include_loopback=True
        )

        print(
            f"[AUDIO] Loopback: "
            f"{self.loopback_mic.name}"
        )

        self.vad = webrtcvad.Vad(2)

        self.frame_samples = int(
            SAMPLE_RATE * FRAME_MS / 1000
        )

        self.silence_frames = int(
            SILENCE_MS / FRAME_MS
        )

        self.min_speech_frames = int(
            MIN_SPEECH_MS / FRAME_MS
        )

        self.max_speech_frames = int(
            MAX_UTTERANCE_SECONDS * 1000 / FRAME_MS
        )

    def _is_speech(self, data):

        mono = data.mean(axis=1)

        mono = np.clip(
            mono,
            -1.0,
            1.0
        )

        pcm = (
            mono * 32767
        ).astype(np.int16)

        return self.vad.is_speech(
            pcm.tobytes(),
            SAMPLE_RATE
        )

    def run(self):

        print("[AUDIO] Recorder start")
        print("[VAD] Czekam na mowę...")

        with self.loopback_mic.recorder(
            samplerate=SAMPLE_RATE
        ) as mic:

            speech_buffer = []

            speech_started = False
            silence_count = 0
            speech_count = 0

            while True:

                data = mic.record(
                    numframes=self.frame_samples
                )

                is_speech = self._is_speech(data)

                if is_speech:

                    if not speech_started:
                        print(
                            "[VAD] Mowa rozpoczęta"
                        )

                    speech_started = True

                    silence_count = 0
                    speech_count += 1

                    speech_buffer.append(data)

                else:

                    if speech_started:

                        # Dodajemy ciszę do bufora,
                        # żeby nie obciąć końca słowa.
                        speech_buffer.append(data)

                        silence_count += 1

                        if (
                            silence_count
                            >= self.silence_frames
                        ):

                            if (
                                speech_count
                                >= self.min_speech_frames
                            ):

                                audio = np.concatenate(
                                    speech_buffer,
                                    axis=0
                                )

                                duration = (
                                    len(audio)
                                    / SAMPLE_RATE
                                )

                                print(
                                    f"[VAD] Koniec wypowiedzi "
                                    f"({duration:.1f}s)"
                                )

                                self.audio_queue.put(
                                    audio
                                )

                            speech_buffer = []
                            speech_started = False
                            silence_count = 0
                            speech_count = 0

                # Maksymalna długość wypowiedzi
                if (
                    speech_started
                    and speech_count
                    >= self.max_speech_frames
                ):

                    audio = np.concatenate(
                        speech_buffer,
                        axis=0
                    )

                    duration = (
                        len(audio)
                        / SAMPLE_RATE
                    )

                    print(
                        f"[VAD] Limit {duration:.1f}s"
                    )

                    self.audio_queue.put(
                        audio
                    )

                    speech_buffer = []
                    speech_started = False
                    silence_count = 0
                    speech_count = 0