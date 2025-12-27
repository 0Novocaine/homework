import asyncio
import argparse
from privat_bank_api_client import PrivatBankAPIClient

BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"
api = PrivatBankAPIClient(BASE_URL)

def check_count(count: str) -> int:
    value = int(count)
    if value < 1 or value > 10:
        raise argparse.ArgumentTypeError(f"Количество дней должно быть от 1 до 10, получено {value}")
    return value

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", type=check_count, required=True, help="Количество дней (1-10)")
    return parser.parse_args()

async def main():
    args = parse_args()
    result = await api.fetch_last_days(args.count)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())