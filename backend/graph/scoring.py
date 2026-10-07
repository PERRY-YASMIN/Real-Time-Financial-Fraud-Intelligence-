def min_max_normalize(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """Normalize a value to the range [0, 1]."""

    if maximum <= minimum:
        return 0.0

    normalized = (value - minimum) / (maximum - minimum)

    return max(0.0, min(normalized, 1.0))