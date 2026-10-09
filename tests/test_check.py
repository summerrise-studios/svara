from pathlib import Path

from svara import cli
from svara.check import check
from svara.song import parse

SONG = """# title: Test
# credit: test text
[pallavi]
చందమామ రావే
జాబిల్లి రావే
చందమామ రావే
"""
EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "brahmam-okkate"


def draft(*singable):
    return {"lines": [{"n": i + 1, "meaning": "m", "singable": s} for i, s in enumerate(singable)]}


def test_parse_sections_meta_repeats_and_rhyme():
    song = parse(SONG)
    assert song.title == "Test"
    assert [l.section for l in song.lines] == ["pallavi"] * 3
    assert song.lines[2].repeat_of == 1
    assert [l.rhyme for l in song.lines] == ["A", "A", "A"]
    assert [song.target(l) for l in song.lines] == [6, 5, 6]


def test_lines_that_fit_pass():
    r = check(parse(SONG), draft("come to me, moon, come to me", "come down, moon, to me", "come to me, moon, come to me"))
    assert r.ok, [l.problems for l in r.lines]


def test_syllable_miss_needs_fixing():
    r = check(parse(SONG), draft("moon", "come down, moon, to me", "moon"))
    assert not r.ok
    assert "too few" in r.lines[0].problems[0]


def test_tolerance_can_be_widened():
    r = check(parse(SONG), draft("come to me, moon", "come down, moon, to me", "come to me, moon"), tolerance=2)
    assert r.ok


def test_refrain_must_repeat():
    r = check(parse(SONG), draft("come to me, moon, come to me", "come down, moon, to me", "moon, come to me, come to me"))
    assert any("repeat" in p for p in r.lines[2].problems)


def test_lost_rhyme_is_a_warning_not_a_failure():
    r = check(parse(SONG), draft("come to me, moon, come to me", "come down, moonlight, come down", "come to me, moon, come to me"))
    assert r.ok
    assert r.lines[1].status == "warn"


def test_missing_line_needs_fixing():
    r = check(parse(SONG), {"lines": [{"n": 1, "singable": "come to me, moon, come to me"}]})
    assert [l.status for l in r.lines][1:] == ["fix", "fix"]


def test_example_translation_passes_and_report_is_written(tmp_path, capsys):
    song, tr = str(EXAMPLE / "song.te.txt"), str(EXAMPLE / "translation.json")
    assert cli.main(["check", song, tr]) == 0
    out = tmp_path / "report.md"
    assert cli.main(["report", song, tr, "-o", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "| # | Telugu |" in text and "Brahmam Okkate" in text


def test_check_exits_1_when_lines_need_fixing(tmp_path):
    song = tmp_path / "s.txt"
    song.write_text(SONG, encoding="utf-8")
    tr = tmp_path / "t.json"
    tr.write_text('{"lines": [{"n": 1, "singable": "moon"}]}', encoding="utf-8")
    assert cli.main(["check", str(song), str(tr)]) == 1


def test_analyse_json(capsys):
    assert cli.main(["analyse", str(EXAMPLE / "song.te.txt"), "--json"]) == 0
    assert '"target_syllables": 12' in capsys.readouterr().out
