import re
from pathlib import Path


class FilenameSanitizer:
    @classmethod
    def sanitize(cls, path: Path) -> Path:
        name: str = path.name
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[-\s]+", "-", name)
        return path.with_name(name)
