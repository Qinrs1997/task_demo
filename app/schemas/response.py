from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """Unified API response, similar to base-apivue/backend."""

    code: int = Field(default=200, description="状态码")
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="success", description="消息")
    data: T | None = Field(default=None, description="数据")
