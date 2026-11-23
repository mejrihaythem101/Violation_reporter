"""
schemas.py
----------
The shared "language" of the project: small data containers that modules
pass to each other. No logic here, only structure.

  Utterance : one thing the driver said          (made by speech_to_text.py)
  ParsedCommand : what the parser understood      (made by command_parser.py)
  Incident  : one complete violation case         (grows as it moves through the pipeline)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Utterance:
    """One sentence/phrase spoken by the driver, already transcribed."""
    text: str
    started_at: float                 # time.time() when the driver STARTED speaking
    ended_at: float                   # time.time() when the driver stopped
    audio_path: Optional[str] = None  # .wav of what the mic heard (debug / evidence)

    @property
    def duration(self) -> float:
        return self.ended_at - self.started_at


# Fields the parser tries to fill from what the driver says.
CORE_FIELDS = ("color", "make", "model", "vehicle_type", "position", "violation")


@dataclass
class ParsedCommand:
    """
    What command_parser.py understood from a piece of text.
    Every detail is None when the driver didn't say it.
    """
    raw_text: str                           # exactly what was transcribed
    is_trigger: bool = False                # did it contain the trigger phrase?
    trigger_phrase: Optional[str] = None    # which phrase matched
    color: Optional[str] = None             # "blue"
    shade: Optional[str] = None             # "dark" / "light"
    make: Optional[str] = None              # "Kia"
    model: Optional[str] = None             # "Rio"
    vehicle_type: Optional[str] = None      # "car", "suv", "truck", ...
    position: Optional[str] = None          # "left_shoulder", ...
    violation: Optional[str] = None         # "speeding", ...

    def details(self) -> dict:
        """Only the details that were actually found."""
        return {f: getattr(self, f) for f in CORE_FIELDS + ("shade",)
                if getattr(self, f)}

    def missing(self) -> list:
        """Core details the driver did not mention."""
        return [f for f in CORE_FIELDS if not getattr(self, f)]

    def merge(self, other: "ParsedCommand") -> None:
        """
        Fill the EMPTY details of this command from another one.
        Used when the driver says the trigger and the description in
        two separate sentences. Already-known details are never overwritten.
        """
        for f in CORE_FIELDS + ("shade",):
            if not getattr(self, f) and getattr(other, f):
                setattr(self, f, getattr(other, f))
        self.raw_text = f"{self.raw_text} | {other.raw_text}"


@dataclass
class Incident:
    """
    One violation case. Every module reads from it and writes into it.
    Most fields stay empty until the module responsible for them has run.
    """
    incident_id: str
    trigger_time: float                         # when the driver said the trigger phrase
    trigger_text: str = ""                      # what exactly was said (speech_to_text)
    description_text: str = ""                  # the driver's description (speech_to_text)
    parsed: Optional[ParsedCommand] = None      # color, make, position... (command_parser)
    video_path: Optional[str] = None            # saved clip (capture/recording step)
    selected_track_id: Optional[int] = None     # the violating car (target_selector)
    match_confidence: Optional[float] = None    # how sure we are (target_selector)
    annotated_video_path: Optional[str] = None  # video with the red box
    crop_path: Optional[str] = None             # cropped image of the car
    report_dir: Optional[str] = None            # final folder (incident_report)
