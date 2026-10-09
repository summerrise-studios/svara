import pytest

from svara.telugu import aksharas, analyse


def split(line):
    return [a.text for a in aksharas(line)]


def test_splits_conjuncts_into_the_syllable_they_start():
    assert split("బ్రహ్మమొక్కటే") == ["బ్ర", "హ్మ", "మొ", "క్క", "టే"]


def test_independent_vowels_and_anusvara():
    assert split("అందరికి") == ["అం", "ద", "రి", "కి"]


def test_word_final_consonant_closes_the_previous_syllable():
    a = aksharas("మనస్")
    assert [x.text for x in a] == ["మ", "నస్"]
    assert a[1].guru


@pytest.mark.parametrize(
    "line, pattern",
    [
        ("రాముడు", "UII"),  # long vowel
        ("అందరికి", "UIII"),  # anusvara
        ("బ్రహ్మ", "UI"),  # syllable before a conjunct
        ("కమల", "III"),
    ],
)
def test_laghu_guru(line, pattern):
    assert analyse(line).pattern == pattern


def test_conjunct_in_the_next_word_does_not_make_this_syllable_heavy():
    assert analyse("అందరికి శ్రీ").pattern == "UIIIU"


def test_counts_and_matras():
    a = analyse("చందమామ రావే")
    assert a.count == 6
    assert a.matras == 2 + 1 + 2 + 1 + 2 + 2


def test_prasa_is_the_second_syllables_consonant():
    assert analyse("కందువగు హీనాధికము").prasa == "ద"
    assert analyse("బ్రహ్మమొక్కటే").prasa == "హ్మ"


def test_ignores_latin_text_and_punctuation():
    assert analyse("రావే, (x2)").count == 2


def test_empty_line():
    a = analyse("")
    assert a.count == 0 and a.prasa == "" and a.end_rhyme == ""
