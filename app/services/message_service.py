from app.services.repository_service import BaseRepository
from app.database.mongodb import get_messages_collection
from app.models.messages import Message
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional,List,Dict

class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_messages_collection(), Message)
    

    def update_message_event_reference(
        self, 
        message_id: str, 
        event_id: str
    ):
        self.collection.find_one_and_update(
            {"_id": ObjectId(message_id)},
            {
                "$set": {
                    "event_id": ObjectId(event_id)
                }
            }
        )
    
    async def get_messages_count_by_time(
        self,
        time_range: str = "1d",  # пример: "1h", "2h", "1d", "3d" и т.д.
        interval: str = "5m",    # пример: "1m", "5m", "15m", "1h" и т.д.
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, int]]:
        """
        Возвращает количество сообщений по временным интервалам.
        
        Args:
            time_range: Общий диапазон времени (например, "2h" - последние 2 часа)
            interval: Интервал группировки (например, "5m" - каждые 5 минут)
            start_time: Начальная дата/время (если не указано, вычисляется из time_range)
            end_time: Конечная дата/время (по умолчанию текущее время)
            
        Returns:
            Список словарей с ключами "timestamp" и "count"
        """
        # Парсим параметры времени
        now = datetime.now()
        
        if end_time is None:
            end_time = now
            
        if start_time is None:
            time_value = int(time_range[:-1])
            time_unit = time_range[-1]
            
            if time_unit == 'm':
                delta = timedelta(minutes=time_value)
            elif time_unit == 'h':
                delta = timedelta(hours=time_value)
            elif time_unit == 'd':
                delta = timedelta(days=time_value)
            else:
                raise ValueError(f"Unknown time unit: {time_unit}")
                
            start_time = end_time - delta
            
        # Парсим интервал
        interval_value = int(interval[:-1])
        interval_unit = interval[-1]
        
        if interval_unit == 'm':
            interval_seconds = interval_value * 60
        elif interval_unit == 'h':
            interval_seconds = interval_value * 3600
        else:
            raise ValueError(f"Unknown interval unit: {interval_unit}")
        
        # Создаем агрегационный pipeline
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": start_time,
                        "$lte": end_time
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$subtract": [
                            { "$toLong": "$created_at" },
                            { "$mod": [{ "$toLong": "$created_at" }, interval_seconds * 1000] }
                        ]
                    },
                    "count": { "$sum": 1 }
                }
            },
            {
                "$sort": { "_id": 1 }
            },
            {
                "$project": {
                    "timestamp": {
                        "$toDate": "$_id"
                    },
                    "count": 1,
                    "_id": 0
                }
            }
        ]
        
        # Выполняем запрос
        cursor = self.collection.aggregate(pipeline)
        results = cursor.to_list(length=None)
        
        return results