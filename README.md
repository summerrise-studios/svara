<img src=".github/banner.png" alt="Svara — song translation, by Summer Rise Studios" width="100%">

<p>
  <a href="LICENSE"><img alt="License: AGPL-3.0" src="https://img.shields.io/badge/license-AGPL--3.0-ff7445?style=flat-square"></a>
  <img alt="Status: early prototype" src="https://img.shields.io/badge/status-early%20prototype-5e5a53?style=flat-square">
  <a href="https://github.com/summerrise-studios/svara/actions/workflows/tests.yml"><img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/summerrise-studios/svara/tests.yml?branch=main&label=tests&style=flat-square"></a>
  <a href="https://www.summerrise.studio"><img alt="Website: summerrise.studio" src="https://img.shields.io/badge/web-summerrise.studio-11100f?style=flat-square"></a>
</p>

# Svara

**Translate the feeling, not just the words.**

Svara is researching how a song can keep its rhythm, rhyme, and emotion as it crosses languages — starting with Telugu to English.

## What we're working on

A translated song has to get three things right at once:

- **Rhythm:** the new line has to fit the melody it's sung to.
- **Rhyme:** the rhyme scheme should survive the change of language.
- **Emotion:** the feeling of the original has to carry over, not just its dictionary meaning.

## The prototype

The first prototype translates Telugu songs into English you can sing to the
same tune. It splits the work in two:

- **Claude writes the lines.** In [Claude Code](https://claude.com/claude-code),
  the [`svara` skill](.claude/skills/svara/SKILL.md) has Claude draft a literal
  meaning and a singable English line for every Telugu line.
- **The `svara` tool measures them.** It counts Telugu aksharas (syllables),
  marks laghu/guru weights, prāsa and end rhyme, then counts English syllables
  and flags every line that is too long or short, breaks a refrain, or loses a
  rhyme. Claude revises those lines and checks again.

The result is a table a lyricist can review: original, meaning, singable line,
syllables against target, rhyme, and notes on what was traded away. See the
worked example, Annamacharya's *Brahmam Okkate*:
[song](examples/brahmam-okkate/song.te.txt) ·
[translation](examples/brahmam-okkate/translation.json) ·
[report](examples/brahmam-okkate/report.md).

### Try it

Needs Python 3.10 or newer. There are no other dependencies.

```bash
git clone https://github.com/summerrise-studios/svara.git
cd svara
pip install -e .
svara analyse examples/brahmam-okkate/song.te.txt
svara check examples/brahmam-okkate/song.te.txt examples/brahmam-okkate/translation.json
svara report examples/brahmam-okkate/song.te.txt examples/brahmam-okkate/translation.json
```

To translate your own song, open the repository in Claude Code and ask:
*"Use the svara skill to translate songs/my-song.te.txt"*.

For more accurate English syllables and rhymes, install the CMU Pronouncing
Dictionary extra: `pip install -e ".[cmu]"`.

### Limits

- English syllables are counted by a spelling heuristic unless the CMU extra is
  installed, so a count can be off by one. Hyphenate a word to force its split.
- Telugu weights follow classical rules, simplified: conjuncts only count
  inside a word, and the రేఫ exceptions aren't modelled.
- It matches syllable counts, not the melody itself. Stress-to-beat alignment
  from a recording is the next research step.
- Only use lyrics you own, have permission for, or that are in the public domain.

## Status

**Early prototype.** The analysis and checking work and are tested; the
translation step runs through Claude Code. Watch this repository, or
[join the list](https://www.summerrise.studio/#contact) to hear about demos,
releases and research notes.

## Contributing

Ideas, feedback, and research pointers are welcome: [open an issue](https://github.com/summerrise-studios/svara/issues/new/choose). Please read the [contributing guide](https://github.com/summerrise-studios/.github/blob/main/CONTRIBUTING.md) and [code of conduct](https://github.com/summerrise-studios/.github/blob/main/CODE_OF_CONDUCT.md) first. To report a security problem, follow the [security policy](https://github.com/summerrise-studios/.github/blob/main/SECURITY.md).

## License

Svara is open source under the [GNU Affero General Public License v3.0](LICENSE).
You can use, study, change, and share it. If you run a modified version as a
network service, you must offer its users the source code of your changes.

For hosted plans, support, or commercial licensing, contact
[jampanikomal@summerrise.studio](mailto:jampanikomal@summerrise.studio).

---

Built by [Summer Rise Studios](https://www.summerrise.studio) · [LinkedIn](https://www.linkedin.com/company/summerrise-studios) · [X](https://x.com/SummerRiseStudi) · [Instagram](https://www.instagram.com/summerrisestudios/)
