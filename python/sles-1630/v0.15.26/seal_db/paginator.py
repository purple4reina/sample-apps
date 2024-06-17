import asyncio
import typing

import asyncpg  # type: ignore[import]
from seal_logging import logger
from sqlalchemy import ColumnElement, ScalarResult, UnaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.sql.selectable import CompoundSelect, Select

from .authentication import Service as AuthenticationService
from .settings import PaginationSettings

T = typing.TypeVar("T")


class Paginator:
    def __init__(
        self,
        session_factory: typing.Callable[..., AsyncSession],
        settings: PaginationSettings,
        # (#860rhf1aa) for debugging the occasional authentication failure
        authentication_service: AuthenticationService,
    ):
        self._session_factory = session_factory
        self._settings = settings
        self._authentication_service = authentication_service

    async def _fetch_results(
        self,
        query: typing.Union[Select[typing.Tuple[T]], CompoundSelect],
        count_query: typing.Optional[Select[typing.Tuple[T]]],
    ) -> typing.Tuple[int, ScalarResult[T]]:
        async with self._session_factory() as data_query_session, self._session_factory() as count_query_session:
            promises = [
                data_query_session.execute(query)
            ]  # always execute the original query

            if count_query is not None:
                # to run 2 queries in parallel we need 2 sessions - https://github.com/sqlalchemy/sqlalchemy/discussions/9312
                promises.append(count_query_session.execute(count_query))

            data_result, *count_result_list = await asyncio.gather(*promises)

            # optionally grab output from count query
            count_output = count_result_list[0].scalar_one() if count_result_list else 0

            return count_output, data_result.unique().scalars()

    async def get_page(
        self,
        query: typing.Union[Select[typing.Tuple[T]], CompoundSelect],
        # pagination
        offset: typing.Optional[int],
        limit: typing.Optional[int],
        order_by: typing.List[
            typing.Union[ColumnElement[typing.Any], UnaryExpression[typing.Any]]
        ] = [],
        return_count: bool = True,
        add_columns: bool = True,
        distinct: bool = True,
    ) -> typing.Tuple[int, ScalarResult[T]]:
        """Executes a SELECT query on the database and returns a tuple containing the total count of records
        that match the query, and the records themselves. Applies distinct to the results.

        Args:
            query: An SQLAlchemy SELECT statement representing the query to be executed.
            offset: An optional integer representing the number of records to skip before starting to return records.
            limit: An optional integer representing the maximum number of records to return.
            order_by: A tuple of SQLAlchemy expressions used to specify the order in which records should be returned.
                Do not append an ORDER BY clause to queries since it causes wrong results, use this argument instead.
                Only relevent for Select type queries
            return_count: will issue an additional count query for the original results
            add_columns: will add the order_by columns to the query
            distinct: will add distinct to query
        Returns:
            A tuple containing the total count of records that match the query and a SQLAlchemy ScalarResult object
            representing the records themselves.
        """
        # manipulate columns to include order_by
        if len(query._order_by_clauses) > 0:
            raise ValueError(f"Expecting queries with no ORDER BY clause; got {query}")

        if isinstance(query, Select):
            # the following operations cannot be performed on CompoundSelect
            query = query.order_by(None)
            if order_by and add_columns:
                columns = [
                    element_or_expression.element
                    if isinstance(element_or_expression, UnaryExpression)
                    else element_or_expression
                    for element_or_expression in order_by
                ]
                query = query.add_columns(*columns)  # type: ignore[arg-type]
            if distinct:
                query = query.distinct()

        # count before pagination
        count_query = None
        if return_count:
            count_query = select(
                query.subquery()  # Using subquery to count the distinct records -> SELECT count(*) FROM (SELECT DISTINCT ...)
            ).with_only_columns(func.count(), maintain_column_froms=True)

        # pagination and ordering
        if offset is not None and offset > 0:
            query = query.offset(offset=offset)
        if limit is None or limit > self._settings.max_page_size:
            limit = self._settings.limit
        query = query.limit(limit=limit).order_by(*order_by)

        try:
            return await self._fetch_results(query=query, count_query=count_query)
        except (
            asyncpg.exceptions._base.InternalClientError,
            asyncpg.exceptions.InvalidPasswordError,
        ) as e:
            raise e
