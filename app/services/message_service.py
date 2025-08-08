from app.services.repository_service import BaseRepository
from app.database.mongodb import get_messages_collection
from app.models.messages import Message
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

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
    
    async def get_messages_count_by_minute(
        self,
        minutes_back: int = 60,
        event_id: Optional[str] = None
    ) -> list[dict]:
        """Группирует сообщения по минутам (синхронная версия)"""
        try:
            # 1. Подготовка времени
            start_time = datetime.now() - timedelta(minutes=minutes_back)
            print(f"[DEBUG] Фильтр: created_at >= {start_time}")

            # 2. Формируем запрос
            match_query = {"created_at": {"$gte": start_time}}
            if event_id:
                match_query["event_id"] = ObjectId(event_id)

            # 3. Проверяем, есть ли подходящие документы
            test_count = self.collection.count_documents(match_query)
            print(f"[DEBUG] Найдено документов: {test_count}")

            if test_count == 0:
                return []

            # 4. Агрегационный pipeline (исправленная версия)
            pipeline = [
                {"$match": match_query},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"},
                        "hour": {"$hour": "$created_at"},
                        "minute": {"$minute": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}},
                {"$project": {
                    "_id": 0,
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d %H:%M",
                            "date": {
                                "$dateFromParts": {
                                    "year": "$_id.year",
                                    "month": "$_id.month",
                                    "day": "$_id.day",
                                    "hour": "$_id.hour",
                                    "minute": "$_id.minute"
                                }
                            }
                        }
                    },
                    "count": 1
                }}
            ]

            # 5. Выполняем агрегацию
            result = list(self.collection.aggregate(pipeline))
            print(f"[DEBUG] Получено {len(result)} записей")
            return result

        except Exception as e:
            print(f"[ERROR] Ошибка в get_messages_count_by_minute: {str(e)}")
            raise  # Перебрасываем исключение дальше