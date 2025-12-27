import asyncio
import logging
import names
from datetime import datetime
from websockets import serve
from websockets.exceptions import ConnectionClosedOK
from aiofile import AIOFile, Writer
from privat_bank_api_client import PrivatBankAPIClient

BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"
api = PrivatBankAPIClient(BASE_URL)

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()
    log_file_path = "exchange_log.txt"

    def __init__(self):
        self.afp: AIOFile | None = None
        self.writer: Writer | None = None

    async def init_logger(self):
        # открываем файл один раз для добавления записей
        self.afp = await AIOFile(self.log_file_path, mode='a').__aenter__()
        self.writer = Writer(self.afp)

    async def register(self, ws):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f"{ws.name} connected from {ws.remote_address}")

    async def unregister(self, ws):
        self.clients.remove(ws)
        logging.info(f"{ws.name} disconnected")

    async def send_to_clients(self, message: str):
        if self.clients:
            await asyncio.gather(*[client.send(message) for client in self.clients])

    async def ws_handler(self, ws):
        await self.register(ws)
        try:
            async for message in ws:
                await self.process_message(ws, message)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def process_message(self, ws, message: str):
        parts = message.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        if cmd == "exchange":
            days = 1
            if len(parts) > 1:
                try:
                    days = int(parts[1])
                except ValueError:
                    await ws.send("Введите число дней от 1 до 10")
                    return

            if days < 1 or days > 10:
                await ws.send("Количество дней должно быть от 1 до 10")
                return

            await self.send_exchange(ws, days)
            await self.log_exchange(ws.name, days)
        else:
            await self.send_to_clients(f"{ws.name}: {message}")

    async def send_exchange(self, ws, days: int):
        result = await api.fetch_last_days(days)
        text = f"💱 Курсы валют за последние {days} дней:<br><br>"
        for day_data in result:
            for date_str, rates in day_data.items():
                text += f"📅 {date_str}<br>"
                for cur, info in rates.items():
                    text += f"&nbsp;&nbsp;{cur}: покупка {info['purchase']}, продажа {info['sale']}<br>"
                text += "<br>"
        await ws.send(text)

    async def log_exchange(self, username: str, days: int):
        line = f"{datetime.now()} - {username} запросил exchange {days} дней\n"
        if self.writer:
            await self.writer(line)
            await self.afp.fsync()


async def main():
    server = Server()
    await server.init_logger()  # инициализация логирования один раз
    logging.info("WebSocket server started on ws://localhost:8080")
    async with serve(server.ws_handler, "localhost", 8080):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())