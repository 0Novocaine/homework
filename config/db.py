from os import environ
import dotenv

dotenv.load_dotenv()
# print(dotenv.find_dotenv())


user = environ['POSTGRES_USER']
password = environ['POSTGRES_PASSWORD']
host = environ['POSTGRES_HOST']
port = environ['POSTGRES_PORT']
db_name = environ['POSTGRES_DB']

DATABASE_URL = (f"postgresql://"
                f"{user}:"
                f"{password}@"
                f"{host}:"
                f"{port}/"
                f"{db_name}")