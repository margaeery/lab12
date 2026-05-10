import enum


class Season(enum.Enum):
    PEAK = 1
    SHOULDER = 2
    OFF_SEASON = 3
    NORMAL = 4


class ExtraService(enum.Enum):
    BREAKFAST = 1
    PARKING = 2
    SPA = 3


SEASON_MULTIPLIERS = {
    Season.PEAK: 1.5,
    Season.SHOULDER: 1.2,
    Season.OFF_SEASON: 0.8,
    Season.NORMAL: 1.0,
}

SEASON_TAX_RATES = {
    Season.PEAK: 0.1,
    Season.SHOULDER: 0.05,
    Season.OFF_SEASON: 0.0,
    Season.NORMAL: 0.0,
}

EXTRA_BASE_FEES = {
    ExtraService.BREAKFAST: 1000.0,
    ExtraService.PARKING: 500.0,
    ExtraService.SPA: 1500.0,
}

EXTRA_ADDITIONAL_FEES = {
    ExtraService.BREAKFAST: 200.0,
    ExtraService.PARKING: 100.0,
    ExtraService.SPA: 0.0,
}

EXTRA_FINAL_FEES = {
    ExtraService.BREAKFAST: 50.0,
    ExtraService.PARKING: 25.0,
    ExtraService.SPA: 0.0,
}

GUEST_TIERED_RATES = [(2, 500.0), (4, 300.0), (6, 200.0)]
GUEST_FLAT_FEES = [(2, 100.0), (4, 150.0), (6, 200.0)]
GUEST_FINAL_FEES = [(2, 50.0), (4, 75.0), (6, 100.0)]
DURATION_DISCOUNTS = [(30, 0.85), (14, 0.9), (7, 0.95)]
DURATION_BONUSES = [(30, 300.0), (14, 200.0), (7, 100.0)]
PRICE_TIER_SURCHARGES = [(1000.0, 200.0), (2000.0, 100.0), (3000.0, 50.0)]
DIVISIBILITY_DISCOUNTS = [(7, 500.0), (5, 300.0), (3, 100.0)]


def _guest_tiered_surcharge(guests: int) -> float:
    return sum((guests - t) * r for t, r in GUEST_TIERED_RATES if guests > t)


def _guest_flat_fee(guests: int) -> float:
    return sum(f for t, f in GUEST_FLAT_FEES if guests > t)


def _guest_final_fee(guests: int) -> float:
    return sum(f for t, f in GUEST_FINAL_FEES if guests > t)


def _duration_discount(nights: int, amount: float) -> float:
    for threshold, multiplier in DURATION_DISCOUNTS:
        if nights > threshold:
            return amount * (1 - multiplier)
    return 0.0


def _duration_bonus(nights: int) -> float:
    for threshold, bonus in DURATION_BONUSES:
        if nights > threshold:
            return bonus
    return 0.0


def _price_tier_surcharge(price_per_night: float) -> float:
    for threshold, surcharge in PRICE_TIER_SURCHARGES:
        if price_per_night < threshold:
            return surcharge
    return 0.0


def _divisibility_discount(nights: int) -> float:
    for divisor, discount in DIVISIBILITY_DISCOUNTS:
        if nights % divisor == 0:
            return discount
    return 0.0


def calculate_total_cost(
    price_per_night: float,
    nights: int,
    guests: int,
    season: Season,
    extra_service: ExtraService | None = None,
) -> float:
    if price_per_night <= 0:
        raise ValueError("price_per_night must be positive")
    if nights <= 0:
        raise ValueError("nights must be positive")
    if guests <= 0:
        raise ValueError("guests must be positive")

    total = price_per_night * nights
    total += _guest_tiered_surcharge(guests)

    if extra_service:
        total += EXTRA_BASE_FEES.get(extra_service, 0.0)

    total *= SEASON_MULTIPLIERS.get(season, 1.0)
    total -= _duration_discount(nights, total)
    total += _price_tier_surcharge(price_per_night)
    total += total * SEASON_TAX_RATES.get(season, 0.0)
    total += _guest_flat_fee(guests)
    total -= _divisibility_discount(nights)

    if extra_service:
        total += EXTRA_ADDITIONAL_FEES.get(extra_service, 0.0)
        total += EXTRA_FINAL_FEES.get(extra_service, 0.0)

    total += _duration_bonus(nights)
    total += _guest_final_fee(guests)

    return round(total, 2)