import json
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from app.config import settings
from app.services.journal_service import JournalService
from app.models.messages import RawMessage

import asyncio

journal = JournalService()

async def process_message(message: AbstractIncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            #check requirements fields
            if data.get('host') and data.get('message'):
                raw_message = RawMessage(ip=data['host'],text=data['message'])
                await journal.handle(raw_message)

        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")


async def start_incident_consumer():
    """Запускает асинхронного потребителя RabbitMQ для обработки"""
    # Подключение к RabbitMQ
    connection = await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD
    )
    
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(
            'alerts',
            durable=False
        )
        print("Consumer подключен к", f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
        await queue.consume(process_message)
        
        # Бесконечный цикл ожидания сообщений
        await asyncio.Future()

async def run_consumer():
    """Запускает потребитель в asyncio event loop."""
    await start_incident_consumer()

def start_consumer_thread():
    """Запускает потребитель в отдельном потоке."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_consumer())

if __name__ == "__main__":
    asyncio.run(run_consumer())