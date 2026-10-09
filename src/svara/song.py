"""Read a song file and work out what each translated line has to hit.

Song file format (plain UTF-8 text):

    # title: Brahmam Okkate
    # credit: Annamacharya (15th century, public domain)
    [pallavi]
    first line
    second line

    [charanam 1]
    ...

Lines starting with ``#`` are metadata, ``[name]`` starts a section, blank
lines are ignored. Every other line is one sung line.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import telugu

SECTION = re.compile(r"^\[(.+)\]$")
META = re.compile(r"^#\s*([\w-]+)\s*:\s*(.*)$")


@dataclass
class Line:
    n: int
    section: str
    text: str
    analysis: telugu.LineAnalysis
    rhyme: str = ""  # letter in the end-rhyme scheme, e.g. "A"
    repeat_of: int | None = None  # earlier line with the same words


@dataclass
class Song:
    title: str
    meta: dict[str, str]
    lines: list[Line] = field(default_factory=list)

    def target(self, line: Line) -> int:
        return line.analysis.count


def _letters():
    for i in range(26 * 26):
        yield chr(65 + i) if i < 26 else chr(65 + i // 26 - 1) + chr(65 + i % 26)


def parse(text: str) -> Song:
    meta: dict[str, str] = {}
    section = ""
    lines: list[Line] = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if m := META.match(s):
            meta[m.group(1).lower()] = m.group(2).strip()
            continue
        if m := SECTION.match(s):
            section = m.group(1).strip()
            continue
        lines.append(Line(n=len(lines) + 1, section=section, text=s, analysis=telugu.analyse(s)))

    seen: dict[str, int] = {}
    for line in lines:
        key = re.sub(r"\s+", " ", line.text)
        first = seen.setdefault(key, line.n)
        line.repeat_of = first if first != line.n else None

    # Lines whose last akshara matches share a letter; a line with no partner gets "-".
    ends = [line.analysis.end_rhyme for line in lines]
    letters = _letters()
    scheme: dict[str, str] = {}
    for line, end in zip(lines, ends):
        if ends.count(end) < 2:
            line.rhyme = "-"
            continue
        if end not in scheme:
            scheme[end] = next(letters)
        line.rhyme = scheme[end]
    return Song(title=meta.get("title", "Untitled"), meta=meta, lines=lines)


def load(path: str | Path) -> Song:
    return parse(Path(path).read_text(encoding="utf-8"))


def brief(song: Song) -> dict:
    """The analysis a translator (human or Claude) works from, as plain data."""
    return {
        "title": song.title,
        "meta": song.meta,
        "lines": [
            {
                "n": line.n,
                "section": line.section,
                "telugu": line.text,
                "aksharas": line.analysis.split,
                "target_syllables": song.target(line),
                "matras": line.analysis.matras,
                "weights": line.analysis.pattern,
                "prasa": line.analysis.prasa,
                "end_rhyme": line.rhyme,
                "repeat_of": line.repeat_of,
            }
            for line in song.lines
        ],
    }
