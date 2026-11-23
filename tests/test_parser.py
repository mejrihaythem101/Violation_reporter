"""
Step 2 test: does the parser understand typed sentences? (No microphone needed.)

Run from the project root:
    python -m tests.test_parser

Part 1 runs a table of sentences and checks the result.
Part 2 lets you type your own sentences.

HOW TO GROW IT: every time Whisper mis-writes something in a real test, add
that exact sentence to CASES with what the parser SHOULD have understood.
"""
from command_parser import CommandParser

# (sentence, expected). Only the fields listed in `expected` are checked.
# "trigger" is True/False; the other keys are ParsedCommand fields.
CASES = [
    # ---- trigger phrase ---------------------------------------------------
    ("take a photo", {"trigger": True}),
    ("Take a photo.", {"trigger": True}),
    ("take a foto", {"trigger": True}),
    ("take photo", {"trigger": True}),
    ("take a picture", {"trigger": True}),
    ("take the photo", {"trigger": True}),
    ("report violation", {"trigger": True}),
    ("what time is it", {"trigger": False}),
    ("the weather is nice today", {"trigger": False}),
    ("I took a photo of my lunch", {"trigger": False}),

    # ---- trigger + details in ONE sentence -------------------------------
    ("Take a photo, blue Kia on the left shoulder.",
     {"trigger": True, "color": "blue", "make": "Kia", "position": "left_shoulder"}),

    # ---- details only (description as a separate sentence) ---------------
    ("white Toyota Yaris on the right shoulder, speeding",
     {"trigger": False, "color": "white", "make": "Toyota", "model": "Yaris",
      "position": "right_shoulder", "violation": "speeding"}),
    ("Dark blue Kia Rio, left shoulder",
     {"color": "blue", "shade": "dark", "make": "Kia", "model": "Rio",
      "position": "left_shoulder"}),
    ("A grey Hyundai i10 overtaking on the right shoulder",
     {"color": "grey", "make": "Hyundai", "model": "i10",
      "position": "right_shoulder", "violation": "illegal_overtaking"}),
    ("gray Hyundai i 20 on my left",
     {"color": "grey", "make": "Hyundai", "model": "i20", "position": "left"}),

    # ---- traps ------------------------------------------------------------
    ("red Peugeot 208 ran a red light",
     {"color": "red", "make": "Peugeot", "model": "208", "violation": "red_light"}),
    ("Peugeot 208 ran a red light",
     {"color": None, "make": "Peugeot", "model": "208", "violation": "red_light"}),
    ("black Toyata Yarris on the shoulder on the left",
     {"color": "black", "make": "Toyota", "model": "Yaris",
      "position": "left_shoulder"}),
    ("white Toyota Hilux pickup",
     {"color": "white", "make": "Toyota", "model": "Hilux", "vehicle_type": "pickup"}),
    ("a white Hilux",
     {"color": "white", "make": "Toyota", "model": "Hilux"}),
    ("light blue Kea on the right shoulder",
     {"color": "blue", "shade": "light", "make": "Kia", "position": "right_shoulder"}),
    ("silver Mercedes Benz truck in the middle lane",
     {"color": "silver", "make": "Mercedes-Benz", "vehicle_type": "truck",
      "position": "center_lane"}),
    ("white van parked on the emergency lane",
     {"color": "white", "vehicle_type": "van", "position": "shoulder",
      "violation": "illegal_parking"}),
    ("the car is a green Renault Clio",
     {"color": "green", "make": "Renault", "model": "Clio", "vehicle_type": "car"}),
    ("green pickup, the car in front of me",
     {"vehicle_type": "pickup", "position": "ahead"}),
    ("blue Hyundai going the wrong way",
     {"color": "blue", "make": "Hyundai", "violation": "wrong_way"}),
    ("orange motorbike driving on the shoulder",
     {"color": "orange", "vehicle_type": "motorcycle", "position": "shoulder",
      "violation": "shoulder_driving"}),
    ("all right then",
     {"trigger": False, "position": None}),
]


def check(parser: CommandParser, sentence: str, expected: dict) -> list:
    """Return a list of problems (empty list = test passed)."""
    result = parser.parse(sentence)
    problems = []
    for key, want in expected.items():
        got = result.is_trigger if key == "trigger" else getattr(result, key)
        if got != want:
            problems.append(f"{key}: expected {want!r}, got {got!r}")
    return problems


def main() -> None:
    parser = CommandParser()

    passed = 0
    for sentence, expected in CASES:
        problems = check(parser, sentence, expected)
        if problems:
            print(f"FAIL  {sentence!r}")
            for p in problems:
                print(f"        - {p}")
        else:
            passed += 1
            print(f"ok    {sentence!r}")
    print(f"\n{passed}/{len(CASES)} tests passed.")

    print("\nNow type your own sentences (empty line to quit):")
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            break
        if not text:
            break
        r = parser.parse(text)
        print(f"   trigger : {r.is_trigger}"
              + (f"  (matched: {r.trigger_phrase!r})" if r.is_trigger else ""))
        print(f"   details : {r.details() or '-'}")
        print(f"   missing : {r.missing()}")


if __name__ == "__main__":
    main()
