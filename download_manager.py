# download_manager.py
import asyncio, httpx, hashlib
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class DownloadTask:
    url: str
    dest: str
    crc: str|None = None
    on_progress: Callable[[int,int], None]|None = None  # bytes, total
    on_done: Callable[[str|None], None]|None = None     # error message or None
    _cancel: asyncio.Event = field(default_factory=asyncio.Event, init=False)

    def cancel(self): self._cancel.set()

class DownloadManager:
    def __init__(self, concurrency:int=4, timeout:float=30.0):
        limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
        self.client = httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True)
        self.semaphore = asyncio.Semaphore(concurrency)

    async def close(self): await self.client.aclose()

    async def run(self, tasks:list[DownloadTask]):
        await asyncio.gather(*(self._run_task(t) for t in tasks))

    async def _run_task(self, t:DownloadTask):
        async with self.semaphore:
            if t._cancel.is_set():
                if t.on_done: t.on_done("cancelled"); return
            try:
                async with self.client.stream("GET", t.url) as resp:
                    resp.raise_for_status()
                    total = int(resp.headers.get("Content-Length") or 0)
                    done = 0
                    h = hashlib.crc32(b"") if t.crc else None  # placeholder, real CRC32 via zlib
                    with open(t.dest, "wb") as f:
                        async for chunk in resp.aiter_bytes():
                            if t._cancel.is_set():
                                if t.on_done: t.on_done("cancelled"); return
                            f.write(chunk); done += len(chunk)
                            if t.on_progress: t.on_progress(done, total)
                    # TODO: echte CRC32 prüfen, hier nur Platzhalter
                    if t.on_done: t.on_done(None)
            except Exception as e:
                if t.on_done: t.on_done(str(e))
