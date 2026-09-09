from __future__ import annotations

import argparse
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import uvicorn


_RECORDING_ENV_KEYS = (
    "AGROFIELD_PROVIDER",
    "AGROFIELD_DB_PATH",
    "AGROFIELD_RECORDING_MODE",
    "NEBIUS_API_KEY",
    "TAVILY_API_KEY",
)


@contextmanager
def recording_environment(enabled: bool) -> Iterator[Path | None]:
    """Isolate a rehearsal from persistent data and external providers."""
    if not enabled:
        yield None
        return

    previous = {key: os.environ.get(key) for key in _RECORDING_ENV_KEYS}
    with TemporaryDirectory(prefix="agrofield-recording-") as directory:
        database_path = Path(directory) / "agrofield-recording.sqlite3"
        os.environ.update(
            {
                "AGROFIELD_PROVIDER": "local",
                "AGROFIELD_DB_PATH": str(database_path),
                "AGROFIELD_RECORDING_MODE": "1",
                "NEBIUS_API_KEY": "",
                "TAVILY_API_KEY": "",
            }
        )
        try:
            yield database_path
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AgroField Agent locally")
    parser.add_argument(
        "--recording",
        action="store_true",
        help="use a fresh synthetic database and disable external providers",
    )
    args = parser.parse_args()
    with recording_environment(args.recording) as database_path:
        if database_path:
            print("Recording rehearsal: fresh synthetic data, local provider, Tavily off.")
        uvicorn.run(
            "agrofield_agent.app:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
        )


if __name__ == "__main__":
    main()
