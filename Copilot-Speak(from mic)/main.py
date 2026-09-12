import queue
import threading

from audio_recorder import AudioRecorder
from transcriber import Transcriber
from translator import Translator
from gui import TranslationGUI
from transcript_logger import TranscriptLogger


def main():

    # ============================================================
    # Kolejki
    # ============================================================

    audio_queue = queue.Queue()
    text_queue = queue.Queue()
    translation_queue = queue.Queue()

    # ============================================================
    # Komponenty
    # ============================================================

    recorder = AudioRecorder(
        audio_queue
    )

    transcriber = Transcriber(
        audio_queue,
        text_queue
    )

    translator = Translator()


    logger = TranscriptLogger()

    # ============================================================
    # Whisper warmup
    # ============================================================

    transcriber.warmup()

    # ============================================================
    # Translator thread
    # ============================================================

    def translation_loop():

        print("[TRANSLATOR] Pętla uruchomiona.")

        while True:

            text_source = text_queue.get()

            if text_source is None:
                break

            try:

                print(f"[TRANSLATOR] PL: {text_source}")

                text_target = translator.translate(
                    text_source
                )

                print(f"[TRANSLATOR] EN: {text_target}")

                # Przekazanie do GUI
                translation_queue.put(
                    (text_source, text_target)
                )

                # Zapis do TXT
                logger.save(
                    text_source,
                    text_target
                )

            except Exception as e:

                print(
                    f"[TRANSLATOR ERROR] {e}"
                )

            finally:
                text_queue.task_done()

    # ============================================================
    # Wątki
    # ============================================================

    recorder_thread = threading.Thread(
        target=recorder.run,
        daemon=True
    )

    transcriber_thread = threading.Thread(
        target=transcriber.run,
        daemon=True
    )

    translator_thread = threading.Thread(
        target=translation_loop,
        daemon=True
    )

    recorder_thread.start()
    transcriber_thread.start()
    translator_thread.start()

    # ============================================================
    # GUI
    # ============================================================

    gui = TranslationGUI(
        translation_queue
    )

    gui.run()


if __name__ == "__main__":
    main()