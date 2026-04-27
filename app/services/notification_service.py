import asyncio
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    async def send_task_completed_email(self, task_id: int) -> None:
        await asyncio.sleep(0)
        logger.info("Email sent for task %s", task_id)
