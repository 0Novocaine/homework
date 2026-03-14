1. Инициировать запуск докер-контейнеров: docker-compose up -d
2. Создание контактов и отправка их в очередь: python producer.py
3. Анализ очереди и заглушка: python consumer.py
4. Проверка обработванных контактов: python check_db.py