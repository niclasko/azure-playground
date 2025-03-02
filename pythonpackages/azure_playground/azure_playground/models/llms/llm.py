import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, cast

import joblib
from _hashlib import HASH
from aiohttp import ClientSession
from azure_playground.utils.app_data import AppData
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, wait_exponential

LLM_CACHE_DIR: Path = Path("llm_cache")


class LLMData(BaseModel):
    index: int = 0


class LLMResponse(BaseModel):
    index: int = 0


class LLM:
    def __init__(self, cache: bool = True) -> None:
        self.cache: bool = cache

    async def completion(self, data: LLMData) -> Dict[str, Any]:
        raise NotImplementedError

    async def _post(
        self, url: str, headers: Dict[str, Any] = {}, payload: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        file: Path = self._file(url, payload)
        response: Dict[str, Any] = self._cached(file) or await self._async_post(
            url, headers, payload
        )
        self._cache(file, response)
        return response

    async def _async_post(
        self, url: str, headers: Dict[str, Any] = {}, payload: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        @retry(
            retry=retry_if_exception_type(Exception),
            wait=wait_exponential(multiplier=1, min=4, max=10),
        )
        async def _inner() -> Dict[str, Any]:
            async with ClientSession() as session:
                async with cast(ClientSession, session).post(
                    url, headers=headers, json=payload
                ) as response:
                    response.raise_for_status()
                    return await response.json()

        return await _inner()

    def _file(self, url: str, payload: Dict[str, Any]) -> Path:
        key: HASH = hashlib.md5()
        key.update(url.encode(encoding="utf-8"))
        key.update(json.dumps(payload).encode(encoding="utf-8"))
        return AppData.folder() / LLM_CACHE_DIR / key.hexdigest()

    def _cached(self, file: Path) -> Optional[Dict[str, Any]]:
        if not self.cache:
            return None
        if file.exists():
            return joblib.load(file)
        return None

    def _cache(self, file: Path, data: Dict[str, Any]) -> None:
        if self.cache:
            file.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(data, file)
