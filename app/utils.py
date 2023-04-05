from typing import Any, Iterable


def validate_fields_exists_in_dict(fields: Iterable[str], data: dict[str, Any], source_name: str="body"):
    missing_fields: list[str] = []
    for field in fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        # можно также использовать ExceptionGroup здесь
        raise ValueError(f"Field {', '.join(missing_fields)} is missing in {source_name}")