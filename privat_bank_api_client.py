import aiohttp
import asyncio
from datetime import datetime, timedelta
from urllib.parse import urlencode
from typing import List, Dict, Any, Optional
from base_currency_api_client import BaseCurrencyAPIClient


class PrivatBankAPIClient(BaseCurrencyAPIClient):
    def __init__(self, base_url: str, currencies: Optional[List[str]] = None) -> None:
        super().__init__(base_url)
        self.currencies: List[str] = currencies or ["USD", "EUR"]

    def date_injector(self, date_str: str) -> str:
        return f"{self.base_url}?{urlencode({'date': date_str})}"

    @staticmethod
    def generate_dates(days: int) -> List[str]:
        current_date = datetime.now().date()
        return [(current_date - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(days)]

    def filter_rates(self, data: Dict[str, Any], currencies: Optional[List[str]] = None) -> Dict[str, Any]:
        currencies = currencies or self.currencies
        filtered_currencies: Dict[str, Dict[str, Optional[float]]] = {}
        for rate in data.get("exchangeRate", []):
            if rate.get("currency") in currencies:
                sale: Optional[float] = rate.get("saleRate") or rate.get("saleRateNB")
                purchase: Optional[float] = rate.get("purchaseRate") or rate.get("purchaseRateNB")
                filtered_currencies[rate["currency"]] = {"sale": sale, "purchase": purchase}
        return filtered_currencies

    async def fetch_rate(self, session: aiohttp.ClientSession, date_str: str) -> Dict[str, Any]:
        url: str = self.date_injector(date_str)
        async with session.get(url) as response:
            data: Dict[str, Any] = await response.json()
            return {date_str: self.filter_rates(data)}

    async def fetch_last_days(self, days: int) -> List[Dict[str, Dict[str, Optional[float]]]]:
        dates: List[str] = self.generate_dates(days)
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_rate(session, d) for d in dates]
            return await asyncio.gather(*tasks)
