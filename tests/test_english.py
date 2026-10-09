import pytest

from svara.english import rhyme_key, syllables


@pytest.mark.parametrize(
    "word, n",
    [
        ("love", 1), ("loved", 1), ("wanted", 2), ("needed", 2), ("burned", 1),
        ("times", 1), ("kisses", 2), ("pages", 2), ("little", 2), ("table", 2),
        ("smile", 1), ("free", 1), ("blue", 1), ("eyes", 1), ("played", 1),
        ("being", 2), ("flying", 2), ("lion", 2), ("India", 3), ("nation", 2),
        ("creature", 2), ("beside", 2), ("silken", 2), ("every", 2), ("tonight", 2),
        ("I'm", 1), ("don't", 1), ("you're", 1),
    ],
)
def test_word_syllables(word, n):
    assert syllables(word) == n


def test_hyphens_count_each_part():
    assert syllables("tan-da-na-na a-hi") == 6


def test_line_syllables():
    assert syllables("The Truth is only one, the Highest Truth is one") == 12


@pytest.mark.parametrize(
    "a, b",
    [("night", "light"), ("day", "they"), ("one", "sun"), ("sky", "high"), ("soul", "whole"), ("free", "me")],
)
def test_rhymes(a, b):
    assert rhyme_key(f"over the {a}") == rhyme_key(f"under the {b}")


@pytest.mark.parametrize("a, b", [("night", "day"), ("happy", "sky"), ("love", "move")])
def test_non_rhymes(a, b):
    assert rhyme_key(a) != rhyme_key(b)
