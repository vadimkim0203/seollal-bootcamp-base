import abc
from typing import Any, Sequence, Tuple

from sqlalchemy import (
    ColumnElement,
    CursorResult,
    Delete,
    Insert,
    RowMapping,
    Select,
    Table,
    UnaryExpression,
    Update,
    func,
    literal_column,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.dml import ReturningInsert, ReturningUpdate


class Repository(abc.ABC):
    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError()

    @abc.abstractmethod
    async def insert(self, data: dict) -> RowMapping:
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self, id: int, data: dict) -> RowMapping:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_one(self, id: int) -> RowMapping | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_count(self, select_statement: Select, filters: list) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    async def paginate(
        self,
        select_statement: Select,
        filters: list[ColumnElement[bool]],
        ordering: list[UnaryExpression[Any]],
        offset: int,
        size: int,
    ) -> Sequence[RowMapping]:
        raise NotImplementedError()


class SqlAlchemyRepository(Repository):
    def __init__(self, db: AsyncConnection, table: Table):
        super().__init__()
        self.db = db
        self.table = table

    async def commit(self):
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()

    async def insert(self, data: dict) -> RowMapping:
        # Use the table object to help identify the columns to be inserted
        # Dump our model to a dictionary for SQLAlchemy to map the attributes to columns
        # Then return all columns
        insert_statement: ReturningInsert[Tuple] = self.table.insert().values(data).returning(literal_column("*"))
        self._get_compiled_query(insert_statement)
        # Run the insert. Don't forget to await!
        result_records: CursorResult = await self.db.execute(insert_statement)
        # mappings() to map the results back to a dictionary
        # first() because we want the first (only) result
        return result_records.mappings().first()
        # The "RowMapping" class supplies Python mapping (i.e. dictionary) access to the contents of the row.
        # This includes support for testing of containment of specific keys (string column names or objects),
        # as well as iteration of keys, values, and items:

    async def update(self, id: int, data: dict) -> RowMapping:
        update_statement: ReturningUpdate[Tuple] = (
            self.table.update().where(self.table.c.id == id).values(data).returning(literal_column("*"))
        )
        self._get_compiled_query(update_statement)
        result_records: CursorResult = await self.db.execute(update_statement)
        return result_records.mappings().first()

    async def delete(self, id: int) -> None:
        delete_statement: Delete = self.table.delete().where(self.table.c.id == id)
        self._get_compiled_query(delete_statement)
        await self.db.execute(delete_statement)

    async def get_one(self, id: int) -> RowMapping | None:
        select_statement: Select = self.table.select().where(self.table.c.id == id)
        self._get_compiled_query(select_statement)
        result_records: CursorResult = await self.db.execute(select_statement)
        return result_records.mappings().first()

    async def paginate(
        self,
        select_statement: Select,
        filters: list[ColumnElement[bool]],
        ordering: list[UnaryExpression[Any]],
        offset: int,
        size: int,
    ) -> Sequence[RowMapping]:
        if filters:
            select_statement = select_statement.where(*filters)
        if ordering:
            select_statement = select_statement.order_by(*ordering)
        select_statement = select_statement.offset(offset).limit(size)
        self._get_compiled_query(select_statement)
        result_records: CursorResult = await self.db.execute(select_statement)
        return result_records.mappings().all()

    async def get_count(self, select_statement: Select, filters: list) -> int:
        count_select_statement: Select[Tuple[int]] = select(func.count()).select_from(
            select_statement.where(*filters).subquery()
        )
        self._get_compiled_query(count_select_statement)
        result: CursorResult = await self.db.execute(count_select_statement)
        return result.scalar_one_or_none()

    def _get_compiled_query(self, statement: Select | Insert | Update | Delete):
        compiled_query = str(statement.compile(compile_kwargs={"literal_binds": True}))
        print(compiled_query)
