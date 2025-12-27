CLI (запуск из терминала)
Проект поддерживает получение курсов валют напрямую из командной строки за последние N (до 10 включительно) дней. 
Файл cli.py
CLI использует PrivatBankAPIClient и выводит USB/EUR в терминал.
Пример команд:
python cli.py -c 5
python cli.py --count 3

WebSocket Server
Проект получает курсы валют ПриватБанка за последние N (до 10 включительно) дней и отдаёт их через WebSocket-чат на адресе ws://localhost:8080.
Все команды exchange записываются в файл exchange_log.txt в формате: "2025-12-27 17:32:58 - Username запросил exchange 5 дней"
Примеры команд:

exchange 5
exchange 
