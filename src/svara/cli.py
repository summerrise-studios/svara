"""svara command line: analyse a Telugu song, check a draft, write a report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import song as song_mod
from .check import check, load_translation
from .report import markdown


def _print_analysis(song: song_mod.Song) -> None:
    print(f"{song.title}\n")
    section = None
    for line in song.lines:
        if line.section != section:
            section = line.section
            print(f"[{section}]" if section else "")
        a = line.analysis
        extra = f"  (repeats line {line.repeat_of})" if line.repeat_of else ""
        print(f"{line.n:>3}. {line.text}{extra}")
        print(f"     {a.split}")
        print(
            f"     {a.count} aksharas · {a.matras} mātras · {a.pattern} · "
            f"prāsa {a.prasa or '-'} · end rhyme {line.rhyme}"
        )


def _print_check(result) -> None:
    for r in result.lines:
        mark = {"ok": "ok  ", "warn": "warn", "fix": "FIX "}[r.status]
        print(f"{mark} {r.n:>3}. [{r.actual}/{r.target}] {r.singable}")
        for p in r.problems:
            print(f"           - {p}")
        for w in r.warnings:
            print(f"           ~ {w}")
    s = result.summary()
    print(f"\n{s['ok']} ok, {s['warn']} to check, {s['fix']} to fix (tolerance ±{result.tolerance})")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(prog="svara", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyse", aliases=["analyze"], help="syllables, weights and rhyme of each Telugu line")
    a.add_argument("song", type=Path)
    a.add_argument("--json", action="store_true", help="print the translation brief as JSON")

    c = sub.add_parser("check", help="check a draft translation against the song")
    c.add_argument("song", type=Path)
    c.add_argument("translation", type=Path)
    c.add_argument("--tolerance", type=int, help="allowed syllable difference per line (default 1)")
    c.add_argument("--json", action="store_true")

    r = sub.add_parser("report", help="write a Markdown report for a lyricist")
    r.add_argument("song", type=Path)
    r.add_argument("translation", type=Path)
    r.add_argument("--tolerance", type=int)
    r.add_argument("-o", "--output", type=Path, help="write here instead of printing")

    args = p.parse_args(argv)
    song = song_mod.load(args.song)

    if args.cmd in ("analyse", "analyze"):
        if args.json:
            print(json.dumps(song_mod.brief(song), ensure_ascii=False, indent=2))
        else:
            _print_analysis(song)
        return 0

    result = check(song, load_translation(args.translation), args.tolerance)
    if args.cmd == "check":
        if args.json:
            print(json.dumps(
                {
                    "summary": result.summary(),
                    "lines": [
                        {"n": l.n, "status": l.status, "syllables": l.actual, "target": l.target,
                         "problems": l.problems, "warnings": l.warnings}
                        for l in result.lines
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ))
        else:
            _print_check(result)
        return 0 if result.ok else 1

    text = markdown(result)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
