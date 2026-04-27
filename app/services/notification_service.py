import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class NotificationService:
    async def send_task_completed_email(
        self,
        task_id: int,
        title: str,
        description: str | None,
        due_date: datetime,
    ) -> None:
        await asyncio.sleep(0)
        completed_at = datetime.now(timezone.utc)
        logger.info(
            "Email sent for task %s | title=%s | description=%s | "
            "due_date=%s | completed_at=%s",
            task_id,
            title,
            description or "",
            due_date.isoformat(),
            completed_at.isoformat(),
        )
