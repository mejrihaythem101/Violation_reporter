"""
speech_to_text.py
-----------------
Listens to the microphone, cuts the audio into "utterances" (one thing the
driver says), transcribes each one with faster-whisper, and hands it over.

This module ONLY turns voice into text (+ timestamps).
It does NOT decide what the text means: that is command_parser.py's job.

How it works, in 3 layers:
  1. The microphone fills a queue with small 30 ms audio blocks (never blocks,
     so no audio is lost even while Whisper is busy transcribing).
  2. A simple loudness-based voice detector decides when the driver starts and
     stops speaking and groups the blocks into one utterance.
  3. faster-whisper transcribes that utterance to English text.
"""
import logging
import queue
import time
import wave
from collections import deque
from typing import Iterator, Optional

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

import config
from schemas import Utterance

log = logging.getLogger(__name__)


def _rms(block: np.ndarray) -> float:
    """Loudness of one audio block (0.0 = silence, ~0.1 and up = clear speech)."""
    return float(np.sqrt(np.mean(np.square(block))))


def _save_wav(audio: np.ndarray, path) -> None:
    """Save float32 audio (-1..1) as a 16-bit mono .wav file."""
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(config.SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


class SpeechToText:
    def __init__(self) -> None:
        self._block_s = config.BLOCK_MS / 1000
        self._blocksize = int(config.SAMPLE_RATE * self._block_s)
        self._queue: "queue.Queue[tuple[float, np.ndarray]]" = queue.Queue()
        self._threshold = config.VAD_MIN_THRESHOLD

        log.info("Loading Whisper model '%s' (first run downloads it)...",
                 config.WHISPER_MODEL)
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self._model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            download_root=str(config.MODELS_DIR),
        )
        log.info("Model ready.")

    # ------------------------------------------------------------------
    # Layer 1: microphone -> queue
    # ------------------------------------------------------------------
    def _audio_callback(self, indata, frames, time_info, status) -> None:
        """Called by sounddevice every 30 ms in its own thread. Keep it tiny."""
        if status:
            log.warning("Audio status: %s", status)
        # The callback fires when the block has just been captured, so the
        # block STARTED one block-length ago.
        self._queue.put((time.time() - self._block_s, indata[:, 0].copy()))

    def _calibrate(self) -> None:
        """Measure background noise for a moment and set the speech threshold."""
        log.info("Calibrating background noise: stay quiet for %.1f s...",
                 config.VAD_CALIBRATION_S)
        n_blocks = int(config.VAD_CALIBRATION_S / self._block_s)
        levels = [_rms(self._queue.get()[1]) for _ in range(n_blocks)]
        noise_floor = float(np.median(levels))
        self._threshold = max(noise_floor * config.VAD_NOISE_MULTIPLIER,
                              config.VAD_MIN_THRESHOLD)
        log.info("Noise level %.4f -> speech threshold %.4f",
                 noise_floor, self._threshold)

    # ------------------------------------------------------------------
    # Layer 3: audio -> text
    # ------------------------------------------------------------------
    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe a float32, 16 kHz, mono numpy array to English text."""
        segments, _info = self._model.transcribe(
            audio,
            language="en",
            beam_size=config.WHISPER_BEAM_SIZE,
            initial_prompt=config.INITIAL_PROMPT,
            vad_filter=True,                  # Whisper's own silence trimming
            condition_on_previous_text=False,
        )
        # `segments` is lazy: the real work happens while we loop over it.
        return " ".join(seg.text.strip() for seg in segments).strip()

    def _make_utterance(self, audio: np.ndarray, started_at: float,
                        ended_at: float) -> Optional[Utterance]:
        duration = len(audio) / config.SAMPLE_RATE
        if duration < config.MIN_UTTERANCE_S:
            return None

        t0 = time.time()
        text = self.transcribe(audio)
        log.info("Transcribed %.1fs of audio in %.2fs", duration, time.time() - t0)

        if text.lower().strip(" .,!?") in config.IGNORED_TEXTS:
            log.info("Ignored (silence/noise): %r", text)
            return None

        audio_path = None
        if config.SAVE_DEBUG_AUDIO:
            config.DEBUG_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
            audio_path = config.DEBUG_AUDIO_DIR / f"utt_{int(started_at * 1000)}.wav"
            _save_wav(audio, audio_path)

        return Utterance(
            text=text,
            started_at=started_at,
            ended_at=ended_at,
            audio_path=str(audio_path) if audio_path else None,
        )

    # ------------------------------------------------------------------
    # Layer 2: voice activity detection + the public API
    # ------------------------------------------------------------------
    def listen(self) -> Iterator[Utterance]:
        """
        Generator. Runs forever, yielding one Utterance each time the driver
        says something:

            for utterance in stt.listen():
                print(utterance.text)

        Audio keeps being recorded while an utterance is being transcribed,
        so if the driver speaks again right away, nothing is lost: it is
        simply processed next.
        """
        start_blocks = max(1, config.VAD_START_MS // config.BLOCK_MS)
        pre_blocks = config.PRE_ROLL_MS // config.BLOCK_MS
        end_blocks = max(1, config.VAD_END_SILENCE_MS // config.BLOCK_MS)
        max_blocks = int(config.MAX_UTTERANCE_S / self._block_s)

        with sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=self._blocksize,
            device=config.MIC_DEVICE,
            callback=self._audio_callback,
        ):
            self._calibrate()

            recent = deque(maxlen=pre_blocks + start_blocks)  # idle: rolling pre-roll
            speech: list = []                                 # blocks of current utterance
            in_speech = False
            loud_run = 0        # consecutive loud blocks (to confirm a start)
            silence_run = 0     # consecutive quiet blocks (to confirm an end)
            speech_start = 0.0

            log.info("Listening...")
            while True:
                t, block = self._queue.get()
                loud = _rms(block) > self._threshold

                if not in_speech:
                    recent.append((t, block))
                    loud_run = loud_run + 1 if loud else 0
                    if loud_run >= start_blocks:
                        in_speech = True
                        speech_start = recent[-start_blocks][0]   # first loud block
                        speech = [b for _, b in recent]           # includes pre-roll
                        recent.clear()
                        loud_run = 0
                        silence_run = 0
                else:
                    speech.append(block)
                    silence_run = 0 if loud else silence_run + 1
                    if silence_run >= end_blocks or len(speech) >= max_blocks:
                        speech_end = t + self._block_s - silence_run * self._block_s
                        audio = np.concatenate(speech)
                        in_speech = False
                        speech = []
                        silence_run = 0
                        utterance = self._make_utterance(audio, speech_start, speech_end)
                        if utterance is not None:
                            yield utterance
