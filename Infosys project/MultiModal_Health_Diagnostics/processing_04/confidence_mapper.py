def confidence_band(probability):
    """
    Converts probability percentage into human-readable risk band.
    """

    if probability < 30:
        return "Low likelihood"
    elif probability < 60:
        return "Moderate risk"
    else:
        return "High risk"
