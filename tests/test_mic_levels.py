"""
Step 1 test: is the microphone working, and how loud are noise vs speech?

Run from the project root:
    python -m tests.test_mic_levels
"""
import time

import numpy as np
import sounddevice as sd

import config


def main() -> None:
    print("Available audio devices (look for your USB mic):\n")
    print(sd.query_devices())
    print("\nUsing device:", "system default" if config.MIC_DEVICE is None
          else config.MIC_DEVICE)
    print("\nFor 20 seconds: stay quiet for a few seconds, then speak normally.")
    print("Notice the number when quiet (noise) and when talking (speech).\n")

    blocksize = int(config.SAMPLE_RATE * config.BLOCK_MS / 1000)
    level = [0.0]

    def callback(indata, frames, time_info, status):
        level[0] = float(np.sqrt(np.mean(np.square(indata[:, 0]))))

    with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1, dtype="float32",
                        blocksize=blocksize, device=config.MIC_DEVICE,
                        callback=callback):
        end = time.time() + 20
        while time.time() < end:
            bar = "#" * min(60, int(level[0] * 400))
            print(f"{level[0]:.4f} {bar}")
            time.sleep(0.1)


if __name__ == "__main__":
    main()
