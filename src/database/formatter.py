from typing import Any


def format_json(results: list[Any]) -> str:
    output = []
    for row in results:
        if isinstance(row, dict):
            output.append(" | ".join(f"{k}: {v}" for k, v in row.items()))
        else:
            output.append(str(row))
    return "\n".join(output)


def format_markdown(results: list[Any]) -> str:
    if not results:
        return "No results"

    if isinstance(results[0], dict):
        headers = list(results[0].keys()) if results else []
        col_widths = {h: len(h) for h in headers}
        for row in results:
            if isinstance(row, dict):
                for k, v in row.items():
                    col_widths[k] = max(col_widths[k], len(str(v)))

        header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
        separator = " | ".join("-" * col_widths[h] for h in headers)
        rows = []
        for row in results:
            if isinstance(row, dict):
                rows.append(" | ".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers))
        return f"{header_line}\n{separator}\n" + "\n".join(rows)
    else:
        return "\n".join(str(item) for item in results)


def format_results(results: list[Any], format_type: str = "json") -> str:
    if format_type.lower() == "markdown":
        return format_markdown(results)
    return format_json(results)
