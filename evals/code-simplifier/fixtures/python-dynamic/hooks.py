def after_save(value: str) -> str:
    prefix = "saved:"
    result = prefix + value
    return result


def dispatch(name: str, value: str) -> str:
    available = globals()
    selected = available[name]
    output = selected(value)
    return output
