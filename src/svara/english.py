"""English syllable counts and rhyme keys for checking singable lines.

If the optional ``pronouncing`` package (CMU Pronouncing Dictionary) is
installed it is used first; otherwise a spelling heuristic is used. The
heuristic is right for most everyday lyric words; add misses to EXCEPTIONS.
"""

from __future__ import annotations

import re

try:  # optional: pip install "svara[cmu]"
    import pronouncing as _cmu
except ImportError:  # pragma: no cover - depends on the environment
    _cmu = None

EXCEPTIONS = {
    "area": 3, "being": 2, "create": 2, "created": 3, "creation": 3, "diet": 2,
    "every": 2, "everyone": 3, "everything": 3, "fire": 1, "hour": 1, "idea": 3,
    "ideas": 3, "lion": 2, "naive": 2, "our": 1, "people": 2, "piano": 3,
    "poem": 2, "poet": 2, "quiet": 2, "real": 1, "recipe": 3, "science": 2,
    "smile": 1, "the": 1, "video": 3, "whole": 1, "world": 1, "yes": 1,
    "you": 1, "your": 1, "heaven": 2, "heavens": 2, "flower": 2, "power": 2,
    "different": 3, "family": 3, "evening": 2, "being's": 2,
    "deity": 3, "eternal": 3, "soul": 1, "souls": 1, "divine": 2, "one": 1,
    "once": 1, "some": 1, "come": 1, "done": 1, "none": 1, "love": 1, "above": 2,
}

WORD = re.compile(r"[A-Za-z']+")
VOWEL_GROUP = re.compile(r"[aeiouy]+")


def words(line: str) -> list[str]:
    return [w.lower().strip("'") for w in WORD.findall(line.replace("-", " ")) if w.strip("'")]


def _heuristic(word: str) -> int:
    w = word.replace("'", "")
    if not w:
        return 0
    if w in EXCEPTIONS:
        return EXCEPTIONS[w]
    if len(w) <= 3:
        return 1
    n = len(VOWEL_GROUP.findall(w))
    # silent final e: "smile", "fire" — but not "little", "table", "free", "blue"
    if w.endswith("e") and not re.search(r"[^aeiouy]le$", w) and re.search(r"[^aeiouy]e$", w):
        n -= 1
    # "-es": "loves", "times" lose it; "kisses", "boxes", "pages" keep it
    elif re.search(r"[^aeiouy]es$", w) and not re.search(r"(s|x|z|ch|sh|ce|ge)es$|[cg]es$", w):
        n -= 1
    # "-ed": "loved", "burned" lose it; "wanted", "needed" keep it
    elif re.search(r"[^aeiouytd]ed$", w):
        n -= 1
    # vowel-vowel pairs that are two syllables: "lion", "India", "usual", "being"
    n += len(re.findall(r"(?<![cstgx])i[ao]|ua(?!r)|[aeiouy]ing$", w))
    return max(1, n)


def word_syllables(word: str) -> int:
    if _cmu is not None:
        phones = _cmu.phones_for_word(word)
        if phones:
            return _cmu.syllable_count(phones[0])
    return _heuristic(word)


def syllables(line: str) -> int:
    return sum(word_syllables(w) for w in words(line))


# Spelling endings that sound alike, checked in order (consonant endings first).
_RHYME_ENDINGS = [
    (r"(ights?|ites?|ytes?)$", "AIT"),
    (r"(ines?|igns?|ynes?)$", "AIN"),
    (r"(imes?|ymes?)$", "AIM"),
    (r"(ires?|yres?)$", "AIR"),
    (r"(ides?|ied)$", "AID"),
    (r"(eart|art)s?$", "ART"),
    (r"(ones?|owns?|oans?)$", "OHN"),
    (r"(ores?|oors?|ours?|oars?|ors?)$", "OR"),
    (r"(ays|aze|aise|ais|eys)$", "AYZ"),
    (r"(ames?|aims?)$", "AYM"),
    (r"(ains?|anes?|eins?)$", "AYN"),
    (r"(eets?|eats?|etes?)$", "EET"),
    (r"(eels?|eals?)$", "EEL"),
    (r"(eams?|eems?|emes?)$", "EEM"),
    (r"(ools?|ules?)$", "OOL"),
    (r"(ouls?|oles?|oals?|owls?)$", "OHL"),
    (r"(oms?|omes?)$", "OHM"),
    (r"(ees|eas|ies)$", "EEZ"),
    (r"(eigh|ey|ay|ai|ae)$", "AY"),
    (r"(igh|ie|ye)$", "AI"),
    (r"(ee|ea)$", "EE"),
    (r"(oo|ue|ew)$", "OO"),
    (r"(ough|ow|ou)$", "OW"),
]


def rhyme_key(line: str) -> str:
    """A key that two lines share when their last words (probably) rhyme."""
    ws = words(line)
    if not ws:
        return ""
    last = ws[-1]
    if _cmu is not None:
        phones = _cmu.phones_for_word(last)
        if phones:
            return _cmu.rhyming_part(phones[0])
    if re.search(r"[^aeiou]y$", last):  # "sky" vs "happy"
        return "AI" if word_syllables(last) == 1 else "EE"
    if last in {"me", "be", "we", "he", "she", "free"}:
        return "EE"
    if last in {"go", "so", "no", "know", "flow", "show", "grow", "slow", "low", "glow"}:
        return "OH"
    if last in {"do", "to", "you", "who", "true", "through", "new", "two"}:
        return "OO"
    if last in {"one", "done", "none", "won", "begun"}:
        return "un"
    if last in {"love", "above", "of", "glove", "dove"}:
        return "UV"
    for pattern, key in _RHYME_ENDINGS:
        if re.search(pattern, last):
            return key
    m = re.search(r"[aeiouy]+[^aeiouy]*$", last)
    return m.group(0) if m else last
