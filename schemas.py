"""
schemas.py
----------
The shared "language" of the project: small data containers that modules
pass to each other. No logic here, only structure.

  Utterance : one thing the driver said          (made by speech_to_text.py)
  Incident  : one complete violation case         (grows as it moves through the pipeline)
"""
from dataclasses import dataclass, field
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
    parsed: dict = field(default_factory=dict)  # color, make, position... (command_parser)
    video_path: Optional[str] = None            # saved clip (capture/recording step)
    selected_track_id: Optional[int] = None     # the violating car (target_selector)
    match_confidence: Optional[float] = None    # how sure we are (target_selector)
    annotated_video_path: Optional[str] = None  # video with the red box
    crop_path: Optional[str] = None             # cropped image of the car
    report_dir: Optional[str] = None            # final folder (incident_report)
