import abc
from typing import Any, Sequence, Tuple

from sqlalchemy import (
    Delete,
    Result,
    RowMapping,
    Select,
    Table,
    func,
    literal_column,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningInsert, ReturningUpdate


class IRepository(abc.ABC):
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
        filters: list[Any],
        ordering: list[Any],
        offset: int,
        size: int,
    ) -> Sequence[RowMapping]:
        raise NotImplementedError()


class SqlAlchemyRepository(IRepository):
    def __init__(self, db: AsyncSession, table: Table):
        super().__init__()
        self.db = db
        self.table = table

    async def insert(self, data: dict) -> RowMapping:
        insert_statement: ReturningInsert[Tuple] = (
            self.table.insert().values(data).returning(literal_column("*"))
        )
        result_records: Result = await self.db.execute(insert_statement)
        return result_records.mappings().first()

    async def update(self, id: int, data: dict) -> RowMapping:
        update_statement: ReturningUpdate[Tuple] = (
            self.table.update()
            .where(self.table.c.id == id)
            .values(data)
            .returning(literal_column("*"))
        )
        result_records: Result = await self.db.execute(update_statement)
        return result_records.mappings().first()

    async def delete(self, id: int) -> None:
        delete_statement: Delete = self.table.delete().where(self.table.c.id == id)
        await self.db.execute(delete_statement)

    async def get_one(self, id: int) -> RowMapping | None:
        select_statement: Select = self.table.select().where(self.table.c.id == id)
        result_records: Result = await self.db.execute(select_statement)
        return result_records.mappings().first()

    async def paginate(
        self,
        select_statement: Select,
        filters: list[Any],
        ordering: list[Any],
        offset: int,
        size: int,
        scalars: bool,
    ) -> Sequence[RowMapping]:
        if filters:
            select_statement = select_statement.where(*filters)
        if ordering:
            select_statement = select_statement.order_by(*ordering)
        select_statement = select_statement.offset(offset).limit(size)
        result_records: Result = await self.db.execute(select_statement)
        return result_records.mappings().all()

    async def get_count(self, select_statement: Select, filters: list) -> int:
        count_select_statement: Select[Tuple[int]] = select(func.count()).select_from(
            select_statement.where(*filters).subselect_statement()
        )
        result: Result = await self.db.execute(count_select_statement)
        return result.scalar_one_or_none()
