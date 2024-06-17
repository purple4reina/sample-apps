# compatibility with sqlite
import typing

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.compiler import Compiled


@compiles(UUID, "sqlite")  # type: ignore[no-untyped-call,misc]
def compile_binary_sqlite(
    type_: UUID[str], compiler: Compiled, **kw: typing.Any
) -> str:
    return "VARCHAR"
