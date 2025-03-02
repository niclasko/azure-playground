import json
import os
from pathlib import Path
from typing import Any, Dict

from azure_playground.utils.config import APP_NAME


class AppData:
    @classmethod
    def folder(cls) -> str:
        return os.path.expanduser(rf"~\AppData\Local\{APP_NAME}")

    @classmethod
    def write(cls, data: Dict[str, Any], path: Path) -> None:
        os.makedirs(Path(cls.folder(), path).parent, exist_ok=True)
        converted: bytes = json.dumps(data, indent=4).encode("utf-8")
        Path(cls.folder(), path).write_bytes(converted)

    @classmethod
    def read(cls, path: Path) -> Any:
        return json.loads(Path(AppData.folder(), path).read_bytes())
