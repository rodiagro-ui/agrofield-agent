import os

from agrofield_agent.__main__ import recording_environment
from agrofield_agent.config import Settings


def test_recording_environment_is_fresh_local_and_restores_state(monkeypatch):
    monkeypatch.setenv("AGROFIELD_PROVIDER", "nebius")
    monkeypatch.setenv("AGROFIELD_DB_PATH", "persistent.sqlite3")
    monkeypatch.setenv("AGROFIELD_RECORDING_MODE", "0")
    monkeypatch.setenv("NEBIUS_API_KEY", "private-nebius-key")
    monkeypatch.setenv("TAVILY_API_KEY", "private-tavily-key")

    with recording_environment(True) as database_path:
        assert database_path is not None
        temporary_directory = database_path.parent
        settings = Settings.from_env()
        assert settings.provider == "local"
        assert settings.database_path == database_path
        assert settings.recording_mode is True
        assert settings.nebius_api_key is None
        assert settings.tavily_api_key is None
        database_path.touch()
        assert database_path.exists()

    assert not temporary_directory.exists()
    assert os.environ["AGROFIELD_PROVIDER"] == "nebius"
    assert os.environ["AGROFIELD_DB_PATH"] == "persistent.sqlite3"
    assert os.environ["AGROFIELD_RECORDING_MODE"] == "0"
    assert os.environ["NEBIUS_API_KEY"] == "private-nebius-key"
    assert os.environ["TAVILY_API_KEY"] == "private-tavily-key"
