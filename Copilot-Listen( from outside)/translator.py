import time

from deep_translator import GoogleTranslator

from config import (
    TRANSLATION_SOURCE,
    TRANSLATION_TARGET,
)


class Translator:

    def __init__(self):

        self.translator = GoogleTranslator(
            source=TRANSLATION_SOURCE,
            target=TRANSLATION_TARGET
        )

    def translate(self, text):

        if not text.strip():
            return ""

        try:

            result = self.translator.translate(
                text
            )

            if result:
                return result

            return "[Brak tłumaczenia]"

        except Exception as e:

            print(
                f"[TRANSLATOR] Błąd: {e}"
            )

            time.sleep(0.5)

            try:

                result = (
                    self.translator.translate(
                        text
                    )
                )

                if result:
                    return result

            except Exception as retry_error:

                print(
                    "[TRANSLATOR] "
                    f"Retry failed: "
                    f"{retry_error}"
                )

            return "[Nie udało się przetłumaczyć]"