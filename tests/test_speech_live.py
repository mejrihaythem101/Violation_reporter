"""
Step 1 test: live microphone -> text.

Run from the project root:
    python -m tests.test_speech_live

Say things like:
    "take a photo"
    "blue Kia, left shoulder"
    "white Toyota Yaris on the right shoulder, speeding"
Press Ctrl+C to stop.
"""
import logging

from speech_to_text import SpeechToText


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s  %(levelname)s  %(message)s")
    stt = SpeechToText()
    print("\nSpeak after you see 'Listening...'. Ctrl+C to stop.\n")

    try:
        for utt in stt.listen():
            print(f'\n>>> [{utt.duration:.1f}s of speech] "{utt.text}"')

            # TEMPORARY: the real trigger detection will live in command_parser.py
            if "photo" in utt.text.lower():
                print(">>> (placeholder) trigger phrase heard -> an incident would start here")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
