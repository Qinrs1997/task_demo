from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.database import close_db, configure_database, drop_db, init_db
from app.main import create_app


@pytest.fixture
def future_due_date() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()


@pytest.fixture
async def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncClient, None]:
    db_path = tmp_path / "test_tasks.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("API_KEY", "test-secret")

    configure_database(get_settings().DATABASE_URL)
    await init_db()

    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"X-API-Key": "test-secret"},
    ) as test_client:
        yield test_client

    await drop_db()
    await close_db()
