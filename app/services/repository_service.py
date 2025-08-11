from typing import Optional, List, Type, TypeVar
from bson import ObjectId
from datetime import datetime, timedelta
from pydantic import BaseModel
from pymongo.collection import Collection

T = TypeVar('T', bound=BaseModel)

class BaseRepository:
    def __init__(self, collection: Collection, model: Type[T]):
        self.collection = collection
        self.model = model
    
    async def create(self, item: T) -> T:
        item_dict = item.model_dump(by_alias=True, exclude={"id"})
        res = self.collection.insert_one(item_dict)
        item.id = str(res.inserted_id)
        return item

    async def get(self, id: str) -> Optional[T]:
        item_data = self.collection.find_one({"_id": ObjectId(id)})
        return self.model(**item_data) if item_data else None
    
    async def get_list(
        self,
        skip: int = 0,
        limit: int = 10,
        text_search: Optional[str] = None,
        **filters
    ) -> List[T]:
        query = {}

        if text_search:
            query["$text"] = {"$search": text_search}
        
        for field, value in filters.items():
            if value is not None:
                query[field] = value
        
        # Добавляем сортировку по убыванию по полю updated_at
        cursor = self.collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        return [self.model(**item) for item in cursor]
    
    async def get_by_time_period(
        self,
        time_field: str = "created_at",
        hours: Optional[int] = None,
        days: Optional[int] = None,
        minutes: Optional[int] = None,
        sort_desc: bool = True,
        **filters
    ) -> List[T]:
        """
        Получение элементов за определенный период времени.
        
        Args:
            time_field: Поле, по которому фильтруется время (по умолчанию "updated_at")
            hours: Количество часов назад
            days: Количество дней назад
            minutes: Количество минут назад
            sort_desc: Сортировать по убыванию времени (новые сначала)
            filters: Дополнительные фильтры
            
        Returns:
            List[T]: Список элементов, созданных/обновленных за указанный период
        """
        query = {**filters}
        
        now = datetime.now()
        if minutes is not None:
            start_time = now - timedelta(minutes=minutes)
        elif hours is not None:
            start_time = now - timedelta(hours=hours)
        elif days is not None:
            start_time = now - timedelta(days=days)
        else:
            # Если период не указан, возвращаем пустой список
            return []
        
        query[time_field] = {"$gte": start_time}
        
        sort_order = -1 if sort_desc else 1
        cursor = self.collection.find(query).sort(time_field, sort_order)
        return [self.model(**item) for item in cursor]
    
    async def get_count(self, **filters) -> int:
        query = {}
        for field, value in filters.items():
            if value is not None:
                query[field] = value
        return self.collection.count_documents(query)
    
    async def update(self, id: str, update_data: dict) -> Optional[T]:
        update_data = {k: v for k, v in update_data.items() if v is not None}
        update_data.pop("id", None)
        update_data.pop("_id", None)
        update_data.pop("created_at", None)
        
        if not update_data:
            return None
        
        update_data["updated_at"] = datetime.now()

        result = self.collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": update_data},
            return_document=True
        )
        return self.model(**result) if result else None
    
    async def delete(self, id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0