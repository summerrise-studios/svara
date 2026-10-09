"""Write a check result as a Markdown report a lyricist can review."""

from __future__ import annotations

from .check import Result

STATUS = {"ok": "✅ fits", "warn": "⚠️ check", "fix": "❌ fix"}


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def markdown(result: Result) -> str:
    song, t = result.song, result.translation
    s = result.summary()
    out = [f"# {song.title}", ""]
    if credit := song.meta.get("credit"):
        out.append(f"Original: {credit}  ")
    if who := t.get("translator"):
        out.append(f"Singable English: {who}  ")
    out += [
        f"Syllable tolerance: ±{result.tolerance} · "
        f"{s['ok']} of {s['lines']} lines fit, {s['warn']} to check, {s['fix']} to fix",
        "",
        "| # | Telugu | Aksharas | Meaning | Singable English | Syllables | Rhyme | Status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r, line in zip(result.lines, song.lines):
        out.append(
            "| {n} | {te} | {split} | {meaning} | {sing} | {actual} / {target} | {rhyme} | {status} |".format(
                n=r.n,
                te=_cell(r.telugu),
                split=_cell(line.analysis.split),
                meaning=_cell(r.meaning),
                sing=_cell(r.singable),
                actual=r.actual,
                target=r.target,
                rhyme=r.rhyme_letter,
                status=STATUS[r.status],
            )
        )
    notes = [(r.n, n) for r in result.lines for n in r.problems + r.warnings + ([r.notes] if r.notes else [])]
    if notes:
        out += ["", "## Notes", ""]
        out += [f"- **Line {n}:** {_cell(text)}" for n, text in notes]
    if extra := t.get("notes"):
        out += ["", "## Translator's notes", "", extra]
    out += [
        "",
        "---",
        "",
        "Syllables are English syllables / Telugu aksharas. Rhyme letters show which Telugu lines "
        "end alike (`-` = no rhyme partner). Counts are automatic and can be off by one; "
        "a lyricist should sing every line before it is final.",
        "",
    ]
    return "\n".join(out)
