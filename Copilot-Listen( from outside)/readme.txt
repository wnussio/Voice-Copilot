# Meeting Copilot

Aplikacja do **transkrypcji i tłumaczenia mowy w czasie rzeczywistym**.

Program przechwytuje dźwięk systemowy, wykrywa mowę, transkrybuje ją lokalnie za pomocą Whisper uruchomionego na GPU, tłumaczy tekst z angielskiego na polski i wyświetla wynik w GUI.

Dodatkowo każda wypowiedź jest zapisywana do pliku TXT z godziną.

## Architektura

```text
Dźwięk systemowy
       ↓
AudioRecorder + VAD
       ↓
audio_queue
       ↓
Whisper / faster-whisper
       ↓
text_queue
       ↓
Translator
       ↓
EN + PL
    ┌──┴──┐
    ↓     ↓
   GUI   TXT
```

## Funkcje

* przechwytywanie dźwięku systemowego
* Voice Activity Detection (VAD)
* automatyczne wykrywanie początku i końca wypowiedzi
* lokalna transkrypcja za pomocą Whisper
* wykorzystanie GPU NVIDIA przez CUDA
* transkrypcja w języku angielskim
* automatyczne tłumaczenie EN → PL
* wyświetlanie angielskiego i polskiego tekstu w GUI
* automatyczny zapis rozmowy do TXT
* osobny plik TXT dla każdej sesji
* timestamp przy każdej wypowiedzi

## Wymagania

* Windows 10/11
* Python 3.14
* karta NVIDIA z obsługą CUDA
* zalecane minimum 16 GB RAM
* połączenie internetowe wymagane przez Google Translator

## Instalacja

Projekt korzysta z globalnego środowiska Pythona — **venv nie jest wymagane**.

### 1. Instalacja pakietów Python

W PowerShell:

```powershell
python -m pip install numpy scipy soundcard webrtcvad deep-translator faster-whisper
```

### 2. Pakiety NVIDIA

Dla działania Whisper na GPU:

```powershell
python -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

### 3. Sprawdzenie GPU

```powershell
nvidia-smi
```

Powinna pojawić się karta NVIDIA oraz informacja o sterowniku.

### 4. Sprawdzenie faster-whisper

```powershell
python -c "import ctranslate2; print(ctranslate2.get_supported_compute_types('cuda'))"
```

Jeżeli pojawi się między innymi:

```text
float16
float32
int8
```

CUDA jest dostępne dla CTranslate2.

## Uruchomienie

Przejdź do katalogu projektu:

```powershell
cd C:\Users\marci\Desktop\scripter
```

Uruchom:

```powershell
python main.py
```

Przy prawidłowym uruchomieniu program powinien załadować Whisper, wykonać warmup i uruchomić nagrywanie.

## Konfiguracja

Najważniejsze ustawienia znajdują się w:

```text
config.py
```

Przykładowa konfiguracja:

```python
MODEL_SIZE = "small"

SAMPLE_RATE = 48000
WHISPER_SAMPLE_RATE = 16000

FRAME_MS = 30
SILENCE_MS = 700
MIN_SPEECH_MS = 300
MAX_UTTERANCE_SECONDS = 15

WHISPER_LANGUAGE = "en"

WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"

TRANSLATION_SOURCE = "en"
TRANSLATION_TARGET = "pl"
```

### Model Whisper

Można zmienić:

```python
MODEL_SIZE = "tiny"
```

lub:

```python
MODEL_SIZE = "small"
```

`small` daje lepszą jakość transkrypcji kosztem większego czasu przetwarzania.

## Pliki projektu

```text
scripter/
│
├── main.py
├── config.py
├── audio_recorder.py
├── transcriber.py
├── translator.py
├── gui.py
├── transcript_logger.py
│
└── transcript_YYYY-MM-DD_HH-MM-SS.txt
```

### `main.py`

Główny punkt uruchomieniowy aplikacji. Łączy wszystkie komponenty i zarządza kolejkami.

### `config.py`

Konfiguracja programu.

### `audio_recorder.py`

Przechwytywanie dźwięku systemowego i wykrywanie mowy przez VAD.

### `transcriber.py`

Transkrypcja audio za pomocą `faster-whisper`.

### `translator.py`

Tłumaczenie tekstu EN → PL.

### `gui.py`

Interfejs graficzny Tkinter.

### `transcript_logger.py`

Zapisuje transkrypcję i tłumaczenie do pliku TXT.

## Logi transkrypcji

Po uruchomieniu programu tworzony jest nowy plik:

```text
transcript_2026-09-10_18-30-15.txt
```

Przykładowa zawartość:

```text
[18:30:21]
EN: basically.
PL: zasadniczo.

[18:30:25]
EN: And then we move from one level to another.
PL: A następnie przechodzimy z jednego poziomu na drugi.
```

Plik jest zapisywany na bieżąco, więc tekst nie czeka do zakończenia całej sesji.

## CUDA

`transcriber.py` zawiera konfigurację ścieżek do bibliotek CUDA zainstalowanych przez pip.

W obecnej konfiguracji biblioteki znajdują się w:

```text
C:\Users\marci\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\nvidia\
```

W przypadku przeniesienia projektu na inny komputer ścieżka może wymagać zmiany.

## Rozwiązywanie problemów

### `cannot import name 'GUI'`

Jeżeli `gui.py` zawiera:

```python
class TranslationGUI:
```

w `main.py` powinno być:

```python
from gui import TranslationGUI
```

oraz:

```python
gui = TranslationGUI(translation_queue)
```

### `Translator.__init__() takes 1 positional argument but 3 were given`

Aktualny `Translator` nie korzysta z kolejek.

Powinno być:

```python
translator = Translator()
```

### `Path.touch() got an unexpected keyword argument 'encoding'`

`Path.touch()` nie przyjmuje `encoding`.

Powinno być:

```python
self.file_path.touch(exist_ok=True)
```

Kodowanie UTF-8 ustawiane jest podczas właściwego zapisu:

```python
open(
    self.file_path,
    "a",
    encoding="utf-8"
)
```

### `cublas64_12.dll is not found`

Sprawdź instalację:

```powershell
python -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

oraz:

```powershell
nvidia-smi
```

## Uwagi

Whisper działa lokalnie na komputerze użytkownika.

Tekst jest wysyłany do Google Translator przez bibliotekę `deep-translator`, ponieważ tłumaczenie nie jest obecnie wykonywane lokalnym modelem AI.

Program został zaprojektowany jako prosty fundament pod dalszy rozwój Meeting Copilot.
