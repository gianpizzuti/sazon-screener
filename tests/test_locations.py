import pytest

from screener.domain.locations import LocationMatcher
from screener.domain.text import is_grounded


@pytest.fixture(scope="module")
def matcher(config):
    return LocationMatcher(config.service_areas)


@pytest.mark.parametrize(
    "text, city, zone",
    [
        ("Chamberí", "madrid", "Chamberí"),
        ("vivo en chamberi", "madrid", "Chamberí"),       # no accent, lowercase
        ("Madrid", "madrid", None),
        ("Getafe", "madrid", "Getafe"),                    # metro town listed as a zone
        ("Madrid centro", "madrid", "Centro"),
        ("por la Roma Norte", "cdmx", "Cuauhtémoc"),
        ("centro histórico", "cdmx", "Cuauhtémoc"),        # more specific than "centro"
        ("Ciutat Vella, Valencia", "valencia", "Ciutat Vella"),
        ("San Pedro", "monterrey", "San Pedro Garza García"),
    ],
)
def test_resolves_known_places(matcher, text, city, zone):
    match = matcher.match(text)
    assert (match.status, match.city_id, match.zone) == ("resolved", city, zone)


def test_zone_names_shared_by_cities_are_ambiguous(matcher):
    match = matcher.match("Centro")
    assert match.status == "ambiguous"
    assert set(match.option_city_ids) == {"madrid", "malaga", "guadalajara", "monterrey"}


def test_ciutat_vella_alone_is_ambiguous(matcher):
    assert set(matcher.match("Ciutat Vella").option_city_ids) == {"barcelona", "valencia"}


def test_typos_are_tolerated(matcher):
    match = matcher.match("Madriz")
    assert (match.status, match.city_id, match.source) == ("resolved", "madrid", "fuzzy")


@pytest.mark.parametrize("text", ["Toledo", "Salamanca", "Buenos Aires", ""])
def test_unknown_places_are_left_to_the_model(matcher, text):
    # "Salamanca" is a Madrid district *and* a city outside the area: rules don't guess.
    assert matcher.match(text).status == "no_match"


class TestGrounding:
    def test_exact_quote_is_grounded_ignoring_case_and_accents(self):
        assert is_grounded("Tengo carnet", "si, tengo CARNET desde 2019")

    def test_invented_quote_is_not_grounded(self):
        assert not is_grounded("vivo en Madrid", "tengo carnet y moto")

    def test_small_respellings_are_tolerated(self):
        assert is_grounded("dos años en glovo", "llevo dos años en Glovo más o menos")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("en la noche", "es"),                      # the LLM once called this English
        ("full time y part time", "es"),            # Spanish with English loanwords
        ("mañanas y tardes", "es"),
        ("Hi! Can we do this in English?", "en"),
        ("two years with Rappi and a bit of DiDi", "en"),
        ("Sí, I have license de moto", None),       # genuinely mixed: no opinion, the model decides
        ("flexible", None),
        ("Lucía Fernández", None),
    ],
)
def test_function_word_second_opinion(text, expected):
    from screener.domain.text import function_word_language

    assert function_word_language(text) == expected
