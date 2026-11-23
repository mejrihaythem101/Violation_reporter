"""
config.py
---------
ONE place for every setting of the project.
Nothing else in the project should contain "magic numbers": if you want to
change a behaviour (model size, microphone, sensitivity...), you change it here.

Moving from your PC to the Raspberry Pi should mostly mean editing this file.
"""
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"            # Whisper (and later YOLO) weights
OUTPUT_DIR = BASE_DIR / "output"            # incident folders will go here
DEBUG_AUDIO_DIR = OUTPUT_DIR / "debug_audio"

# ----------------------------------------------------------------------------
# Microphone / audio input
# ----------------------------------------------------------------------------
SAMPLE_RATE = 16000     # Whisper expects 16 kHz mono. Do not change.
BLOCK_MS = 30           # audio is processed in blocks of 30 ms
MIC_DEVICE = None       # None = system default mic. Otherwise put the device
                        # number printed by tests/test_mic_levels.py

# ----------------------------------------------------------------------------
# Whisper (faster-whisper)
# ----------------------------------------------------------------------------
# PC:            "base.en" (good balance) or "small.en" (more accurate, slower)
# Raspberry Pi:  "tiny.en"
WHISPER_MODEL = "base.en"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"   # int8 = fastest on CPU, tiny accuracy loss
WHISPER_BEAM_SIZE = 1           # 1 = fastest. 5 = slightly more accurate.

# A "hint" that nudges Whisper toward the words we expect (brands, positions).
# If you ever see this text appear in the output when nobody spoke, shorten it.
INITIAL_PROMPT = (
    "Driver report about a road violation. Examples: take a photo, "
    "report violation, blue Kia Rio, white Toyota Yaris, black Hyundai Accent, "
    "red Peugeot 208, grey Renault Clio, left shoulder, right shoulder, speeding."
)

# Whisper sometimes "invents" short texts from pure noise. Ignore these.
IGNORED_TEXTS = {"", "you", "thank you", "thanks for watching", "bye"}

# ----------------------------------------------------------------------------
# Voice activity detection (decides WHEN the driver is speaking)
# ----------------------------------------------------------------------------
VAD_CALIBRATION_S = 1.5     # at startup: stay quiet so we measure background noise
VAD_NOISE_MULTIPLIER = 3.0  # speech = louder than (noise level x this)
VAD_MIN_THRESHOLD = 0.01    # never go below this loudness threshold
VAD_START_MS = 120          # must be loud for this long to count as speech start
VAD_END_SILENCE_MS = 800    # this much silence = the sentence is finished
PRE_ROLL_MS = 300           # keep this much audio BEFORE speech start (first syllable)
MIN_UTTERANCE_S = 0.5       # ignore anything shorter (clicks, coughs)
MAX_UTTERANCE_S = 12.0      # safety cap for a single utterance

# ----------------------------------------------------------------------------
# Debugging
# ----------------------------------------------------------------------------
SAVE_DEBUG_AUDIO = True     # save each utterance as .wav so you can listen to it
