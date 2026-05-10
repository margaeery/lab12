import pytest

from room_cost_calculator.bad_calculator import f
from room_cost_calculator.calculator import calculate_total_cost, Season, ExtraService


class TestBehaviorMatch:
    @pytest.mark.parametrize(
        "price,nights,guests,season,extra",
        [
            (1000, 1, 1, 4, 0),
            (1000, 3, 1, 1, 0),
            (1000, 3, 1, 3, 0),
            (1000, 3, 4, 4, 0),
            (1000, 3, 7, 4, 0),
            (1000, 8, 1, 4, 0),
            (1000, 15, 1, 4, 0),
            (1000, 31, 1, 4, 0),
            (500, 3, 1, 4, 0),
            (1500, 3, 1, 4, 0),
            (3500, 3, 1, 4, 0),
            (1000, 7, 1, 4, 0),
            (1000, 5, 1, 4, 0),
            (1000, 3, 1, 4, 0),
            (1000, 1, 1, 4, 1),
            (1000, 1, 1, 4, 2),
            (1000, 1, 1, 4, 3),
            (1000, 8, 4, 2, 1),
            (2000, 15, 6, 1, 2),
        ],
    )
    def test_same_result(self, price, nights, guests, season, extra):
        bad = f(price, nights, guests, season, extra)
        season_enum = Season(season)
        extra_enum = ExtraService(extra) if extra else None
        good = calculate_total_cost(price, nights, guests, season_enum, extra_enum)
        assert bad == pytest.approx(good, abs=0.01)


class TestRefactoredValidation:
    def test_zero_price(self):
        with pytest.raises(ValueError, match="price_per_night"):
            calculate_total_cost(0.0, 1, 1, Season.NORMAL)

    def test_negative_nights(self):
        with pytest.raises(ValueError, match="nights"):
            calculate_total_cost(1000.0, -1, 1, Season.NORMAL)

    def test_zero_guests(self):
        with pytest.raises(ValueError, match="guests"):
            calculate_total_cost(1000.0, 1, 0, Season.NORMAL)
