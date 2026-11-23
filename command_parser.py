"""
command_parser.py
-----------------
Turns the driver's words (text) into structured data.

    text  ->  CommandParser.parse()  ->  ParsedCommand
                                          .is_trigger   (did they say "take a photo"?)
                                          .color / .make / .model /
                                          .vehicle_type / .position / .violation

The parser has NO memory and does NOT decide what happens next (start the
recording, wait for more details...). That is main.py's job. Text in, result out:
this makes it very easy to test without a microphone.

Method: rules + dictionaries (vocabulary.py) + a little fuzzy matching to
survive transcription mistakes. No AI model: fast, predictable, easy to debug.
"""
import logging
import re
import unicodedata
from typing import Optional

from rapidfuzz import fuzz, process

import config
import vocabulary
from schemas import ParsedCommand

log = logging.getLogger(__name__)

# Positions that already say everything (side + place).
_COMPOUND_POSITIONS = {"left_shoulder", "right_shoulder", "left_lane",
                       "right_lane", "center_lane"}

# A color followed by one of these is a TRAFFIC light, not the car's color.
_TRAFFIC_WORDS = {"light", "lights", "signal"}


def normalize(text: str) -> str:
    """Lowercase, remove accents and punctuation, collapse spaces."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("_", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _build_table(vocab: dict) -> dict:
    """{"left_shoulder": ["..."]} -> {("left","shoulder"): "left_shoulder", ...}"""
    table = {}
    for canonical, aliases in vocab.items():
        for alias in [canonical, *aliases]:
            key = tuple(normalize(alias).split())
            if key:
                table[key] = canonical
    return table


class CommandParser:
    def __init__(self) -> None:
        self._triggers = [normalize(p) for p in config.TRIGGER_PHRASES]

        self._tables = {
            "color": _build_table(vocabulary.COLORS),
            "make": _build_table(vocabulary.MAKES),
            "model": _build_table({m: v[1] for m, v in vocabulary.MODELS.items()}),
            "vehicle_type": _build_table(vocabulary.VEHICLE_TYPES),
            "position": _build_table(vocabulary.POSITIONS),
            "violation": _build_table(vocabulary.VIOLATIONS),
        }
        # A lone "left"/"right" is too ambiguous ("all right", "turn left").
        # Only full phrases count: "on the left", "left side", "left shoulder"...
        for bare in (("left",), ("right",)):
            self._tables["position"].pop(bare, None)

        self._shade_words = {}
        for shade, aliases in vocabulary.SHADES.items():
            for word in [shade, *aliases]:
                self._shade_words[normalize(word)] = shade
        self._model_to_make = {m: v[0] for m, v in vocabulary.MODELS.items()}

        # Single words that fuzzy matching may compare against (make + model only)
        self._fuzzy_choices = {
            field: {key[0]: canon for key, canon in self._tables[field].items()
                    if len(key) == 1 and len(key[0]) >= config.FUZZY_MIN_WORD_LEN
                    and not key[0].isdigit()}
            for field in ("make", "model")
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def parse(self, text: str) -> ParsedCommand:
        tokens = normalize(text).split()
        result = ParsedCommand(raw_text=text.strip())
        used: set = set()   # token positions already explained by a match

        # 1. Trigger phrase
        phrase = self._detect_trigger(tokens)
        result.is_trigger = phrase is not None
        result.trigger_phrase = phrase

        # 2. Color (+ shade)
        for start, end, canon in self._find(tokens, self._tables["color"]):
            if end < len(tokens) and tokens[end] in _TRAFFIC_WORDS:
                continue                       # "red light" is not the car's color
            result.color = canon
            used.update(range(start, end))
            if start > 0 and tokens[start - 1] in self._shade_words:
                result.shade = self._shade_words[tokens[start - 1]]
            break                              # first color mentioned wins

        # 3. Make and model (exact first, then fuzzy for mis-hearings)
        for field in ("make", "model"):
            matches = self._find(tokens, self._tables[field])
            if matches:
                start, end, canon = matches[0]
                setattr(result, field, canon)
                used.update(range(start, end))
        for field in ("make", "model"):
            if getattr(result, field) is None:
                setattr(result, field, self._fuzzy(tokens, used, field))
        if result.model and not result.make:
            result.make = self._model_to_make.get(result.model)

        # 4. Vehicle type ("car" is generic: any more specific type beats it)
        types = [c for _, _, c in self._find(tokens, self._tables["vehicle_type"])]
        if len(set(types)) > 1:
            types = [t for t in types if t != "car"]
        result.vehicle_type = types[0] if types else None

        # 5. Position
        found = [c for _, _, c in self._find(tokens, self._tables["position"])]
        result.position = self._resolve_position(found)

        # 6. Violation
        violations = self._find(tokens, self._tables["violation"])
        result.violation = violations[0][2] if violations else None

        log.debug("Parsed %r -> trigger=%s %s", text, result.is_trigger, result.details())
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _detect_trigger(self, tokens: list) -> Optional[str]:
        """Slide a window over the words and fuzzy-compare it to each trigger phrase."""
        best_score, best_phrase = 0.0, None
        for phrase in self._triggers:
            n = len(phrase.split())
            for size in range(max(1, n - 1), n + 2):
                for i in range(len(tokens) - size + 1):
                    score = fuzz.ratio(phrase, " ".join(tokens[i:i + size]))
                    if score > best_score:
                        best_score, best_phrase = score, phrase
        if best_score >= config.TRIGGER_MIN_SCORE:
            return best_phrase
        return None

    @staticmethod
    def _find(tokens: list, table: dict) -> list:
        """
        Find every vocabulary phrase in the text. Longer phrases win over
        shorter ones ("left shoulder" beats "left"), and matches never overlap.
        Returns [(start, end, canonical)] in the order they appear.
        """
        max_len = max(len(k) for k in table)
        candidates = []
        for i in range(len(tokens)):
            for n in range(1, min(max_len, len(tokens) - i) + 1):
                canon = table.get(tuple(tokens[i:i + n]))
                if canon is not None:
                    candidates.append((i, i + n, canon))
        candidates.sort(key=lambda m: (-(m[1] - m[0]), m[0]))

        taken: set = set()
        chosen = []
        for start, end, canon in candidates:
            if taken.isdisjoint(range(start, end)):
                taken.update(range(start, end))
                chosen.append((start, end, canon))
        return sorted(chosen)

    def _fuzzy(self, tokens: list, used: set, field: str) -> Optional[str]:
        """Find a word that is CLOSE to a known brand/model ("toyata" -> Toyota)."""
        choices = self._fuzzy_choices[field]
        names = list(choices)
        for i, token in enumerate(tokens):
            if i in used or len(token) < config.FUZZY_MIN_WORD_LEN or token.isdigit():
                continue
            hit = process.extractOne(token, names, scorer=fuzz.ratio,
                                     score_cutoff=config.FUZZY_MIN_SCORE)
            if hit:
                used.add(i)
                return choices[hit[0]]
        return None

    @staticmethod
    def _resolve_position(found: list) -> Optional[str]:
        """Combine what was found into ONE position value."""
        if not found:
            return None
        for canon in found:                    # a complete answer wins
            if canon in _COMPOUND_POSITIONS:
                return canon
        if "shoulder" in found:                # "on the shoulder ... on the left"
            sides = {c for c in found if c in ("left", "right")}
            if len(sides) == 1:
                return f"{sides.pop()}_shoulder"
            return "shoulder"
        return found[0]
