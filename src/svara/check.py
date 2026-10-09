"""Check a draft translation against the song's syllable, refrain and rhyme targets."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from . import english
from .song import Song

DEFAULT_TOLERANCE = 1


@dataclass
class LineResult:
    n: int
    telugu: str
    target: int
    meaning: str = ""
    singable: str = ""
    notes: str = ""
    actual: int = 0
    rhyme_letter: str = "-"
    rhyme_key: str = ""
    problems: list[str] = field(default_factory=list)  # must fix
    warnings: list[str] = field(default_factory=list)  # worth a look

    @property
    def status(self) -> str:
        return "fix" if self.problems else "warn" if self.warnings else "ok"


@dataclass
class Result:
    song: Song
    translation: dict
    tolerance: int
    lines: list[LineResult]

    @property
    def needs_fixing(self) -> list[LineResult]:
        return [r for r in self.lines if r.problems]

    @property
    def ok(self) -> bool:
        return not self.needs_fixing

    def summary(self) -> dict:
        c = Counter(r.status for r in self.lines)
        return {"lines": len(self.lines), "ok": c["ok"], "warn": c["warn"], "fix": c["fix"]}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z']+", " ", s.lower()).strip()


def load_translation(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check(song: Song, translation: dict, tolerance: int | None = None) -> Result:
    if tolerance is None:
        tolerance = int(translation.get("tolerance", DEFAULT_TOLERANCE))
    drafts = {int(d["n"]): d for d in translation.get("lines", [])}
    results: list[LineResult] = []
    by_n: dict[int, LineResult] = {}

    for line in song.lines:
        d = drafts.get(line.n, {})
        r = LineResult(
            n=line.n,
            telugu=line.text,
            target=song.target(line),
            meaning=d.get("meaning", ""),
            singable=d.get("singable", "").strip(),
            notes=d.get("notes", ""),
            rhyme_letter=line.rhyme,
        )
        if not r.singable:
            r.problems.append("no singable line")
        else:
            r.actual = english.syllables(r.singable)
            r.rhyme_key = english.rhyme_key(r.singable)
            diff = r.actual - r.target
            if abs(diff) > tolerance:
                more_less = "too many" if diff > 0 else "too few"
                r.problems.append(f"{r.actual} syllables for {r.target} aksharas ({abs(diff)} {more_less})")
        if not r.meaning:
            r.warnings.append("no literal meaning given")
        if line.repeat_of is not None:
            first = by_n[line.repeat_of]
            if _norm(first.singable) != _norm(r.singable):
                r.problems.append(f"repeats line {line.repeat_of} in Telugu, so it should repeat in English too")
        results.append(r)
        by_n[line.n] = r

    # Lines that rhyme in Telugu should rhyme in English.
    groups: dict[str, list[LineResult]] = {}
    for r, line in zip(results, song.lines):
        if r.rhyme_letter != "-" and r.singable and line.repeat_of is None:
            groups.setdefault(r.rhyme_letter, []).append(r)
    for letter, members in groups.items():
        if len(members) < 2:
            continue
        common, _ = Counter(m.rhyme_key for m in members).most_common(1)[0]
        for m in members:
            if m.rhyme_key != common:
                others = ", ".join(str(o.n) for o in members if o is not m)
                m.warnings.append(f"rhymes with line {others} in Telugu, not in English")

    extra = sorted(set(drafts) - {line.n for line in song.lines})
    if extra:
        raise ValueError(f"translation has lines the song doesn't: {extra}")
    return Result(song=song, translation=translation, tolerance=tolerance, lines=results)
