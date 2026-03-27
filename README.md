0. Установить зависимости;
1. Запустить parser.py для получения данных командой: 
    python parser.py
2. Загрузить данные авторов в базу данных:
python load_authors.py
3. Загрузить цитаты в базу данных:
python load_quotes.py
4. Запустить скрипт поиска:
python search.py
5. Рабочие команды:
    help            -   show this help message
    exit            -   exit program
    
    name:<name>     -   find quotes by author name
    tag:<tag>       -   find quotes by single tag
    tags:<t1,t2>    -   find quotes by multiple tags
    
    all_quotes      -   show all quotes
    all_authors     -   show all  authors
    all_tags        -   show all unique tags
