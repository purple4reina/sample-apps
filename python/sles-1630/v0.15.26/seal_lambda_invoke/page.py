from typing import Generic, Optional, Sequence, TypeVar

from pydantic import BaseModel, NonNegativeInt, PositiveInt

T = TypeVar("T")


class BasePage(BaseModel, Generic[T]):
    items: Sequence[T]


class LimitOffsetPage(BasePage[T], Generic[T]):
    limit: PositiveInt
    offset: NonNegativeInt
    total: NonNegativeInt


class CursorPage(BasePage[T], Generic[T]):
    next_page: Optional[str]
