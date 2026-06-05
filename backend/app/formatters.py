def format_employee_name(
    last_name: str,
    first_name: str,
    middle_name: str | None = None,
) -> str:
    parts = [last_name, first_name]
    if middle_name:
        parts.append(middle_name)
    return " ".join(parts)
