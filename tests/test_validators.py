from datetime import date

from conftest import TODAY, start_expr
from screener.domain.models import Availability, Schedule
from screener.domain.validators import (
    normalize_platforms,
    resolve_start_date,
    validate_availability,
    validate_experience_months,
    validate_full_name,
    validate_schedule,
    validate_start_date,
)


class TestFullName:
    def test_capitalises_lowercase_names_respecting_particles(self):
        assert validate_full_name("maría de la cruz").value == "María de la Cruz"

    def test_keeps_the_candidates_own_casing(self):
        assert validate_full_name("Ana McDonald").value == "Ana McDonald"

    def test_first_name_only_is_kept_but_asks_for_surname(self):
        result = validate_full_name("Ana")
        assert result.value == "Ana" and result.error == "name_needs_surname"

    def test_rejects_things_that_are_not_names(self):
        assert validate_full_name("ana123").error == "name_invalid"
        assert validate_full_name("").error == "name_invalid"


class TestAvailabilityAndSchedule:
    def test_full_and_part_time_together_is_a_contradiction(self):
        assert validate_availability(["full_time", "part_time"]).error == "availability_contradiction"

    def test_weekends_combine_with_either(self):
        assert validate_availability(["part_time", "weekends"]).value == [Availability.PART_TIME, Availability.WEEKENDS]

    def test_empty_availability_is_unclear(self):
        assert validate_availability([]).error == "availability_unclear"

    def test_all_three_shifts_means_flexible(self):
        assert validate_schedule(["morning", "afternoon", "evening"]).value == [Schedule.FLEXIBLE]

    def test_flexible_wins(self):
        assert validate_schedule(["morning", "flexible"]).value == [Schedule.FLEXIBLE]


class TestExperience:
    def test_months_are_kept_exactly(self):
        assert validate_experience_months(8).value == 8

    def test_out_of_range_is_invalid(self):
        assert validate_experience_months(-1).error == "experience_invalid"
        assert validate_experience_months(700).error == "experience_invalid"

    def test_platform_aliases_are_normalised_and_unknown_employers_kept(self, config):
        raw = ["uber", "GLOVO", "Pizzería Luigi", "UberEats"]
        assert normalize_platforms(raw, config.platforms) == ["Uber Eats", "Glovo", "Pizzería Luigi"]


class TestStartDate:
    def test_immediate_is_today(self):
        assert resolve_start_date(start_expr("immediate"), TODAY).value == TODAY

    def test_relative_weeks(self):
        assert resolve_start_date(start_expr("in_weeks", amount=2), TODAY).value == date(2026, 11, 3)

    def test_next_weekday_is_strictly_in_the_future(self):
        assert resolve_start_date(start_expr("next_weekday", weekday=0), TODAY).value == date(2026, 10, 26)
        # "el martes" said on a Tuesday means next week's Tuesday
        assert resolve_start_date(start_expr("next_weekday", weekday=1), TODAY).value == date(2026, 10, 27)

    def test_month_arithmetic_clamps_to_month_end(self):
        assert resolve_start_date(start_expr("in_months", amount=1), date(2027, 1, 31)).value == date(2027, 2, 28)

    def test_vague_answers_are_unclear(self):
        assert resolve_start_date(start_expr("unclear"), TODAY).error == "start_date_unclear"
        assert resolve_start_date(start_expr("exact_date", exact_date="not-a-date"), TODAY).error == "start_date_unclear"

    def test_past_dates_are_rejected_and_far_dates_flagged(self):
        assert validate_start_date(date(2026, 10, 1), TODAY, 90).error == "start_date_past"
        far = validate_start_date(date(2027, 3, 1), TODAY, 90)
        assert far.ok and far.flag == "late_start"


def test_mixed_case_names_get_each_word_capitalised():
    assert validate_full_name("ana López").value == "Ana López"
    assert validate_full_name("JUAN PÉREZ").value == "Juan Pérez"



def test_recent_past_day_month_is_an_error_not_next_year():
    # regression: on 21 Oct, "el 1 de octubre" was accepted as 1 Oct 2027
    resolved = resolve_start_date(start_expr("exact_date", exact_date="2026-10-01"), date(2026, 10, 21))
    assert resolved.value == date(2026, 10, 1)
    assert validate_start_date(resolved.value, date(2026, 10, 21), 90).error == "start_date_past"


def test_far_past_day_month_means_next_year():
    resolved = resolve_start_date(start_expr("exact_date", exact_date="2026-01-10"), date(2026, 12, 20))
    assert resolved.value == date(2027, 1, 10)
