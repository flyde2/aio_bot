import os
import logging
from aiohttp import web
from aiogram import Bot

TELEGRAM_API_TOKEN = "<token>"
BOT_HOST = os.getenv("BOT_HOST", "0.0.0.0")
BOT_PORT = int(os.getenv("BOT_PORT", "8080"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)


async def order_status_webhook(request: web.Request):
    """
    Ожидается POST-запрос с JSON-телом вида:
    {
      "chat_id": <идентификатор_чата>,
      "order_id": <номер заказа>,
      "new_status": <новый статус>,
      "additional_info": <дополнительно, опционально>
    }
    При получении корректных данных бот отправляет уведомление в указанный чат.
    """
    try:
        data = await request.json()
        chat_id = data.get("chat_id")
        order_id = data.get("order_id")
        new_status = data.get("new_status")
        additional_info = data.get("additional_info", "")

        if not (chat_id and order_id and new_status):
            return web.json_response(
                {
                    "error": "Отсутствуют необходимые параметры: "
                             "chat_id, order_id, new_status"},
                status=400
            )

        msg = (f"Статус вашего заказа №{order_id} обновлен!\nНовый статус:"
               f" {new_status}")
        if additional_info:
            msg += f"\nДополнительно: {additional_info}"

        await bot.send_message(chat_id, msg)
        logging.info(
            f"Отправлено уведомление для заказа №{order_id} в чат {chat_id}")
        return web.json_response({"status": "Message sent"})
    except Exception as e:
        logging.exception("Ошибка при обработке webhook запроса:")
        return web.json_response({"error": str(e)}, status=500)


app = web.Application()
app.router.add_post("/webhook/order_status", order_status_webhook)

if __name__ == "__main__":
    logging.info(f"Запуск веб-сервера на http://{BOT_HOST}:{BOT_PORT}/")
    web.run_app(app, host=BOT_HOST, port=BOT_PORT)
