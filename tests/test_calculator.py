import pytest

from room_cost_calculator.bad_calculator import f
from room_cost_calculator.calculator import calculate_total_cost, Season, ExtraService


class TestBehaviorMatch:
    @pytest.mark.parametrize(
        "price,nights,guests,season,extra",
        [
            (1000, 1, 1, Season.NORMAL, None),
            (1000, 3, 1, Season.PEAK, None),
            (1000, 3, 1, Season.OFF_SEASON, None),
            (1000, 3, 4, Season.NORMAL, None),
            (1000, 3, 7, Season.NORMAL, None),
            (1000, 8, 1, Season.NORMAL, None),
            (1000, 15, 1, Season.NORMAL, None),
            (1000, 31, 1, Season.NORMAL, None),
            (500, 3, 1, Season.NORMAL, None),
            (1500, 3, 1, Season.NORMAL, None),
            (3500, 3, 1, Season.NORMAL, None),
            (1000, 7, 1, Season.NORMAL, None),
            (1000, 5, 1, Season.NORMAL, None),
            (1000, 3, 1, Season.NORMAL, None),
            (1000, 1, 1, Season.NORMAL, ExtraService.BREAKFAST),
            (1000, 1, 1, Season.NORMAL, ExtraService.PARKING),
            (1000, 1, 1, Season.NORMAL, ExtraService.SPA),
            (1000, 8, 4, Season.SHOULDER, ExtraService.BREAKFAST),
            (2000, 15, 6, Season.PEAK, ExtraService.PARKING),
        ],
    )
    def test_same_result(self, price, nights, guests, season, extra):
        # bad_calculator ожидает старые числовые значения
        season_num = {"peak": 1, "shoulder": 2, "off_season": 3, "normal": 4}.get(season.value, 4)
        extra_num = {"breakfast": 1, "parking": 2, "spa": 3}.get(extra.value if extra else None, 0)
        bad = f(price, nights, guests, season_num, extra_num)
        good = calculate_total_cost(price, nights, guests, season, extra)
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
