import queue
import tkinter as tk


class TranslationGUI:

    def __init__(
        self,
        translation_queue: queue.Queue
    ):

        self.translation_queue = (
            translation_queue
        )

        self.root = tk.Tk()

        self.root.title(
            "Live tłumaczenie"
        )

        self.root.geometry(
            "700x500"
        )

        self.text_widget = tk.Text(
            self.root,
            wrap="word",
            font=("Arial", 14)
        )

        self.text_widget.pack(
            fill="both",
            expand=True
        )

        self.root.after(
            5, # tutaj jak szybko sie pokaze ms
            self.poll_queue
        )

    def poll_queue(self):

        while not self.translation_queue.empty():

            text_en, text_pl = (
                self.translation_queue.get()
            )

            self.text_widget.insert(
                "end",
                f"PL: {text_en}\n"
            )

            self.text_widget.insert(
                "end",
                f"EN: {text_pl}\n\n"
            )

            self.text_widget.see("end")

        self.root.after(
            5,
            self.poll_queue
        )

    def run(self):

        self.root.mainloop()