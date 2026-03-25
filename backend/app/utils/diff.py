from dataclasses import dataclass


@dataclass
class DiffLine:
    file_path: str
    line_number: int
    content: str


def parse_unified_diff(diff_text: str) -> list[DiffLine]:
    file_path = "unknown"
    new_line_no = 0
    lines: list[DiffLine] = []
    for raw in diff_text.splitlines():
        if raw.startswith("+++ b/"):
            file_path = raw.replace("+++ b/", "", 1)
        elif raw.startswith("@@"):
            segment = raw.split("+")[-1].split(" ")[0]
            new_line_no = int(segment.split(",")[0])
        elif raw.startswith("+") and not raw.startswith("+++"):
            lines.append(DiffLine(file_path=file_path, line_number=new_line_no, content=raw[1:]))
            new_line_no += 1
        elif not raw.startswith("-"):
            new_line_no += 1
    return lines
