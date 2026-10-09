---
name: svara
description: Translate a Telugu song into singable English that keeps each line's syllable count, the refrains and the end rhymes. Use when the user gives a Telugu song or lyric file and wants an English version that can be sung to the same tune.
---

# Svara: singable Telugu → English

You are the translator. The `svara` CLI is your measuring tape: it counts
Telugu aksharas and English syllables and flags refrain and rhyme breaks.
Don't count syllables in your head when the tool can do it.

## 1. Get the song into a file

Put the lyrics in a UTF-8 text file (see `examples/brahmam-okkate/song.te.txt`):

```
# title: Song name
# credit: Writer, year, and whether we may use it
[pallavi]
one sung line per line
[charanam 1]
...
```

Only work on lyrics the user owns, has permission to use, or that are in the
public domain. If the source is a copyrighted film song and they have no
rights, say so and offer to work on a short excerpt or their own lyrics.

## 2. Read the brief

```
python -m svara analyse SONG
```

For each line you get the akshara split, the syllable target, the laghu/guru
pattern, the prāsa consonant, the end-rhyme letter, and which lines repeat
earlier ones.

## 3. Draft `translation.json` next to the song

```json
{
  "title": "...",
  "translator": "Claude in Claude Code, draft for review",
  "tolerance": 1,
  "lines": [
    {"n": 1, "meaning": "literal meaning", "singable": "line to sing", "notes": "optional trade-off"}
  ],
  "notes": "optional notes on the whole song"
}
```

For every line:

- **meaning:** a faithful literal translation. This is the reference for the
  reviewer, so don't pretty it up.
- **singable:** natural English that hits `target_syllables` (within the
  tolerance) and keeps the feeling. Put the stresses where the guru (`U`)
  syllables fall when you can.
- **Refrains:** if `repeat_of` is set, use exactly the same English as that line.
- **Rhyme:** lines with the same end-rhyme letter should end on the same
  English sound. Keeping one refrain word (as the example does with "is one")
  is often the strongest choice.
- **Vocables** (tandanana, ahaa, ...) stay as sung. Hyphenate them
  (`tan-da-na-na`) so each part counts as one syllable.
- **notes:** say what you traded away when you had to choose between meaning,
  syllables and rhyme.

## 4. Check, revise, repeat

```
python -m svara check SONG translation.json
```

Rewrite every `FIX` line and look at every `warn`. Run the check again. Stop
after three rounds and leave a note on any line that still misses, rather than
forcing an awkward line just to hit the count. The English syllable counter is
a heuristic: if it's clearly wrong about a word, say so in the line's notes.

## 5. Hand over the report

```
python -m svara report SONG translation.json -o report.md
```

Show the user the table and the notes. Remind them this is a draft: a
lyricist should sing every line to the tune before it is final.
