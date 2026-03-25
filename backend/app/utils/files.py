from pathlib import Path

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".json",
    ".yml",
    ".yaml",
    ".env",
    ".md",
    ".txt",
    ".ini",
    ".cfg",
    ".toml",
    ".sh",
    "",
}

IGNORE_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv"}


def iter_files(root: str) -> list[Path]:
    files: list[Path] = []
    for path in Path(root).rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            files.append(path)
    return files
