def classify_amount(value: int | None) -> str:
    if value is not None:
        if value != 0:
            if value > 0:
                category = "positive"
            else:
                category = "negative"
        else:
            category = "zero"
    else:
        category = "missing"
    return category
