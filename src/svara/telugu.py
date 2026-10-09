"""Telugu line analysis: aksharas (syllables), laghu/guru weight, prāsa and end rhyme.

An akshara is the written syllable of Telugu: an optional consonant cluster,
a vowel (written or the inherent "a"), and optional anusvara/visarga. Song
lines are sung roughly one akshara per note, so the akshara count is the
syllable budget a singable translation should aim for.

Weights follow classical chandassu, simplified:

* guru (U, 2 mātras): long vowel, anusvara or visarga, a word-final consonant,
  or followed in the same word by a conjunct or doubled consonant;
* laghu (I, 1 mātra): everything else.

Known simplifications: clusters are only counted inside a word, and the
exceptions for some రేఫ (ra) clusters are not modelled.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

VIRAMA = "్"
ANUSVARA = "ం"
VISARGA = "ః"
CANDRABINDU = {"ఀ", "ఁ"}
NUKTA = "఼"
LENGTH_MARKS = {"ౕ", "ౖ"}
JOINERS = {"‌", "‍"}

SHORT_VOWELS = set("అఇఉఋఌఎఒ")
LONG_VOWELS = set("ఆఈఊౠౡఏఐఓఔ")
SHORT_SIGNS = set("ిుృెొౢ")
LONG_SIGNS = set("ాీూౄేైోౌౣ")


def is_consonant(ch: str) -> bool:
    cp = ord(ch)
    return 0x0C15 <= cp <= 0x0C39 or 0x0C58 <= cp <= 0x0C5A or cp == 0x0C5D


def is_telugu(ch: str) -> bool:
    return 0x0C00 <= ord(ch) <= 0x0C7F


@dataclass
class Akshara:
    text: str = ""
    onset: list[str] = field(default_factory=list)
    vowel: str = "అ"  # inherent vowel until a sign or independent vowel says otherwise
    long: bool = False
    anusvara: bool = False
    coda: str = ""  # word-final dead consonant folded into this syllable
    word: int = 0
    guru: bool = False

    @property
    def weight(self) -> str:
        return "U" if self.guru else "I"

    @property
    def matras(self) -> int:
        return 2 if self.guru else 1


def aksharas(line: str) -> list[Akshara]:
    """Split a line of Telugu into aksharas, with laghu/guru weights."""
    line = unicodedata.normalize("NFC", line)
    out: list[Akshara] = []
    cur: Akshara | None = None
    dead = False  # the last consonant of `cur` carries a virama
    word = 0

    def end_word() -> None:
        nonlocal cur, dead, word
        if cur is not None and dead:
            # A word-final consonant with no vowel closes the previous syllable.
            if len(cur.onset) == 1 and len(out) > 1 and out[-2].word == cur.word:
                prev = out[-2]
                prev.coda += cur.text
                prev.text += cur.text
                out.pop()
            else:
                cur.vowel = ""
        if cur is not None:
            word += 1
        cur, dead = None, False

    for ch in line:
        if ch in JOINERS or ch == NUKTA:
            if cur is not None:
                cur.text += ch
            continue
        if not is_telugu(ch):
            end_word()
            continue
        if is_consonant(ch):
            if cur is not None and dead:
                cur.onset.append(ch)
                cur.text += ch
                dead = False
            else:
                cur = Akshara(text=ch, onset=[ch], word=word)
                out.append(cur)
        elif ch in SHORT_VOWELS or ch in LONG_VOWELS:
            if cur is not None and dead:
                end_word()
            cur = Akshara(text=ch, vowel=ch, long=ch in LONG_VOWELS, word=word)
            out.append(cur)
            dead = False
        elif cur is None:
            continue  # stray sign with nothing to attach to
        elif ch == VIRAMA:
            cur.text += ch
            dead = True
        elif ch in SHORT_SIGNS or ch in LONG_SIGNS:
            cur.text += ch
            cur.vowel = ch
            cur.long = ch in LONG_SIGNS
            dead = False
        elif ch in LENGTH_MARKS:
            cur.text += ch
            cur.long = True
        elif ch in (ANUSVARA, VISARGA):
            cur.text += ch
            cur.anusvara = True
        elif ch in CANDRABINDU:
            cur.text += ch  # arasunna does not make the syllable heavy
        else:
            end_word()  # digits, danda and other Telugu-block punctuation
    end_word()

    for i, a in enumerate(out):
        nxt = out[i + 1] if i + 1 < len(out) else None
        cluster_next = nxt is not None and nxt.word == a.word and len(nxt.onset) >= 2
        a.guru = a.long or a.anusvara or bool(a.coda) or cluster_next
    return out


def prasa(syllables: list[Akshara]) -> str:
    """Prāsa key: the consonant(s) of the second akshara ("" if there is none)."""
    if len(syllables) < 2:
        return ""
    return VIRAMA.join(syllables[1].onset)


def end_rhyme(syllables: list[Akshara]) -> str:
    """End-rhyme (antyaprāsa) key: the last akshara as written."""
    return syllables[-1].text if syllables else ""


@dataclass
class LineAnalysis:
    text: str
    syllables: list[Akshara]

    @property
    def count(self) -> int:
        return len(self.syllables)

    @property
    def matras(self) -> int:
        return sum(a.matras for a in self.syllables)

    @property
    def pattern(self) -> str:
        return "".join(a.weight for a in self.syllables)

    @property
    def split(self) -> str:
        return "·".join(a.text for a in self.syllables)

    @property
    def prasa(self) -> str:
        return prasa(self.syllables)

    @property
    def end_rhyme(self) -> str:
        return end_rhyme(self.syllables)


def analyse(line: str) -> LineAnalysis:
    return LineAnalysis(text=line.strip(), syllables=aksharas(line))
