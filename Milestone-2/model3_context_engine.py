def adjust_by_context(row, base_score):
    age = int(row["Age"])
    gender = row["Gender"]

    if age > 60:
        base_score += 1

    if gender.lower() == "male":
        base_score += 0.5

    return base_score
