from datetime import datetime
from pathlib import Path


class TranscriptLogger:

    def __init__(self):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        self.file_path = Path(
            f"transcript_{timestamp}.txt"
        )

        self.file_path.touch(
            exist_ok=True
        )

        print(
            f"[LOG] Zapis transkrypcji: "
            f"{self.file_path}"
        )

    def save(self, text_en, text_pl):

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        content = (
            f"[{timestamp}]\n"
            f"EN: {text_en}\n"
            f"PL: {text_pl}\n\n"
        )

        try:

            with open(
                self.file_path,
                "a",
                encoding="utf-8"
            ) as file:

                file.write(content)

        except Exception as e:

            print(
                f"[LOG ERROR] {e}"
            )